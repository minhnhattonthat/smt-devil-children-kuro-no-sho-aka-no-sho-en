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
    0xFFFA: ('page', 0),
    0xFFF3: ('wait', 0),
    0xFFF0: ('f0', 0),
    0xFFFB: ('fb', 1),       # yes/no prompt; arg low byte = default cursor (renderer 0x800335EC)
    0xFFFC: ('speed', 1),
    0xFFEA: ('ea', 0),
    0xFFEB: ('voice', 1),
    0xFFEE: ('ee', 0),
    0xFFEF: ('face', 1),
    0xFFEC: ('partner', 0),  # partner's name (0x800E091A); see docs/faces.md
    0xFFED: ('ed', 0),
    0xFFF5: ('f5', 0),
    0xFFF6: ('f6', 0),
    0xFFF7: ('f7', 0),
    0xFFF8: ('name', 0),     # hero's (player-entered) name
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
        elif 0x4000 <= v < 0xCCE3 and dec is JP:
            out.append(decode_packed(v))
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


EN_BASE = 0x100   # glyph for ASCII c = 0x100 + c
PACK = 0x4000     # pair unit: PACK | c1 << 7 | c2 (c2 = 0: single char)
TRI = 0x8000      # triple unit: TRI + c1*729 + c2*27 + c3, c = 0 space, 1-26 a-z (0x8000-0xCCE2)
TRI_SET = ' abcdefghijklmnopqrstuvwxyz'  # both decoded by asm/main.asm (pk_head / pk8_head)


def encode_en(text):
    """English -> packed halfwords: lowercase/space triples where possible, else ASCII pairs; {codes} raw."""
    import re
    out = bytearray()
    for m in re.finditer(r'(\{\w+(?::[0-9A-F]{4})*\}|\[[0-9A-F]{4}\])|([^{\[]+|[{\[])', text, re.S):
        if m[1]:
            out += encode(m[1])
            continue
        run = m[2]
        bad = [c for c in run if not 0x20 <= ord(c) < 0x7F]
        assert not bad, 'not ASCII: %r' % ''.join(bad)
        i = 0
        while i < len(run):
            t = run[i:i + 3]
            if len(t) == 3 and all(c in TRI_SET for c in t):
                a, b, c = (TRI_SET.index(x) for x in t)
                out += struct.pack('<H', TRI + a * 729 + b * 27 + c)
                i += 3
            else:
                c2 = ord(run[i + 1]) if i + 1 < len(run) else 0
                out += struct.pack('<H', PACK | ord(run[i]) << 7 | c2)
                i += 2
    return bytes(out)


def decode_packed(v):
    if v >= TRI:
        v -= TRI
        return TRI_SET[v // 729] + TRI_SET[v // 27 % 27] + TRI_SET[v % 27]
    return chr((v >> 7) & 0x7F) + (chr(v & 0x7F) if v & 0x7F else '')


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
