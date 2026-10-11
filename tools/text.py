"""16-bit text codec for Devil Children PS1 (glyph codes LE, FFxx control codes).

  python -X utf8 tools/text.py scan FILE [--min 4] [--align 2]   list decodable strings: offset, length, text
"""
import argparse
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NGLYPH = 0x2E0

# FFxx control codes: name, extra halfwords after the code.  Arg counts from B_MAIN disassembly
# (0x80033AF0 simple draw, 0x800342B4 name/number expander); others unverified -> 0.
CTRL = {
    0xFFFF: ('end', 0),
    0xFFFE: ('n', 0),
    0xFFFD: ('end2', 0),
    0xFFEF: ('ef', 1),
    0xFFEC: ('hero', 0),
    0xFFED: ('ed', 0),
    0xFFF5: ('f5', 0),
    0xFFF6: ('f6', 0),
    0xFFF7: ('f7', 0),
    0xFFF8: ('f8', 0),
    0xFFF9: ('num', 2),
}
CTRL_ENC = {v[0]: (k, v[1]) for k, v in CTRL.items()}


def load_table(path=ROOT / 'tbl' / 'jp.tbl'):
    dec = {}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        k, v = line.split('=', 1)
        base = int(k, 16)
        for i, c in enumerate(v):
            dec[base + i] = c
    return dec


JP = load_table()
JP_ENC = {}
for _k, _v in JP.items():
    JP_ENC.setdefault(_v, _k)


def decode(data, pos, dec=JP, stop_end=True):
    """Decode halfwords from pos through {end}. Returns (text, bytes consumed)."""
    out, p = [], pos
    while p + 2 <= len(data):
        v = struct.unpack_from('<H', data, p)[0]
        p += 2
        if v in CTRL:
            name, argc = CTRL[v]
            args = [struct.unpack_from('<H', data, p + 2 * i)[0] for i in range(argc)]
            p += 2 * argc
            out.append('{%s%s}' % (name, ''.join(':%04X' % a for a in args)))
            if name == 'end' and stop_end:
                break
        elif v in dec:
            out.append(dec[v])
        else:
            out.append('[%04X]' % v)
    return ''.join(out), p - pos


def encode(text, enc=JP_ENC):
    import re
    out = bytearray()
    for m in re.finditer(r'\{(\w+)((?::[0-9A-F]{4})*)\}|\[([0-9A-F]{4})\]|(.)', text, re.S):
        if m[1]:
            code, argc = CTRL_ENC[m[1]]
            args = [int(a, 16) for a in m[2].split(':')[1:]]
            assert len(args) == argc, m[0]
            out += struct.pack('<H', code) + b''.join(struct.pack('<H', a) for a in args)
        elif m[3]:
            out += struct.pack('<H', int(m[3], 16))
        else:
            out += struct.pack('<H', enc[m[4]])
    return bytes(out)


def is_text_unit(v):
    return v < NGLYPH or v in CTRL


def scan(data, minlen=4, align=2):
    """Yield (offset, nbytes, text) for runs of text units ending in FFFF with >= minlen glyphs incl. some kana."""
    n = len(data) // 2 * 2
    p = 0
    while p < n:
        if data[p] == 0 and data[p + 1] == 0:  # skip zero padding (glyph 0 is a space)
            p += 2
            continue
        q = p
        glyphs = kana = 0
        while q + 2 <= n:
            v = struct.unpack_from('<H', data, q)[0]
            if not is_text_unit(v):
                break
            q += 2
            if v in CTRL:
                q += 2 * CTRL[v][1]
                if v == 0xFFFF:
                    break
            else:
                glyphs += 1
                kana += 0x57 <= v < 0x2E0
        if q > p and struct.unpack_from('<H', data, q - 2)[0] == 0xFFFF and glyphs >= minlen and kana * 2 >= glyphs:
            yield p, q - p, decode(data, p)[0]
            p = q
        else:
            # no suffix of a failed run ends differently, so skip it whole (keeps the scan linear)
            p = max(p + align, q)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['scan', 'dec'])
    ap.add_argument('file')
    ap.add_argument('--min', type=int, default=4)
    ap.add_argument('--align', type=int, default=2)
    ap.add_argument('--at', type=lambda s: int(s, 16))
    a = ap.parse_args()
    data = Path(a.file).read_bytes()
    if a.cmd == 'dec':
        print(decode(data, a.at)[0])
        return
    tot = cnt = 0
    for off, ln, t in scan(data, a.min, a.align):
        print('%08X %5d %s' % (off, ln, t))
        tot += ln
        cnt += 1
    print('# %d strings, %d bytes' % (cnt, tot))


if __name__ == '__main__':
    main()
