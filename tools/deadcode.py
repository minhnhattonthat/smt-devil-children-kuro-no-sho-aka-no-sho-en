"""Unreferenced functions of a main EXE: dead code is safe room for patch code (unlike zero BSS "caves").

A function = from an `addiu sp,sp,-N` prologue to the next one. Dead = nothing in the EXE or its overlays refers into it:
no j/jal target, no word in any data that equals an address inside it, no lui + addiu/ori pair building one. Static only:
confirm with tools/lua/execwatch.lua (an exec breakpoint over the range while the game runs a tour).

  python -X utf8 tools/deadcode.py B_MAIN.EXE [min_size]     list dead functions, largest first
  python -X utf8 tools/deadcode.py B_MAIN.EXE refs 0xLO 0xHI  who refers into a range (j/jal/lui pairs/data words)
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TREE = ROOT / 'work/orig/tree'
OVERLAYS = {'B': ['B_EVENT.BIN', 'B_BATTLE.BIN'], 'R': ['R_EVENT.BIN', 'R_BATTLE.BIN'], 'N': []}
EXE_BASE, OV_BASE = 0x80010000, 0x80170000
TEXT_LO = 0x80011000


def _words(d):
    return struct.unpack_from('<%dI' % (len(d) // 4), d)


def references(exe):
    """{address: [(file, offset, kind)]} of every code/data reference to an address in the EXE's RAM range."""
    book = exe[0]
    out = {}
    srcs = [(exe, EXE_BASE, (TREE / exe).read_bytes()[0x800:])] + \
           [(f, OV_BASE, (TREE / f).read_bytes()) for f in OVERLAYS[book]]
    for name, base, d in srcs:
        ws = _words(d)
        for i, w in enumerate(ws):
            op = w >> 26
            if op in (2, 3):
                out.setdefault(((base + i * 4) & 0xF0000000) | ((w & 0x3FFFFFF) << 2), []).append((name, i * 4, 'j/jal'))
            if 0x80010000 <= w < 0x80200000:
                out.setdefault(w, []).append((name, i * 4, 'word'))
            if op == 0x0F and (w & 0xFFFF) >= 0x8000:
                hi, rt = w & 0xFFFF, (w >> 16) & 31
                for j in range(i + 1, min(i + 8, len(ws))):
                    x = ws[j]
                    xop, imm = x >> 26, x & 0xFFFF
                    if xop in (8, 9, 0xD, 0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B) and (x >> 21) & 31 == rt:
                        a = ((hi << 16) + (imm if xop == 0xD else imm - 0x10000 if imm & 0x8000 else imm)) & 0xFFFFFFFF
                        out.setdefault(a, []).append((name, i * 4, 'lui'))
                    if xop in (8, 9, 0xD, 0x0F, 0x20, 0x21, 0x23, 0x24, 0x25) and (x >> 16) & 31 == rt:
                        break
    return out


def functions(exe, text_end):
    d = (TREE / exe).read_bytes()[0x800:]
    starts = [EXE_BASE + i for i in range(TEXT_LO - EXE_BASE, text_end - EXE_BASE, 4)
              if struct.unpack_from('<I', d, i)[0] >> 16 == 0x27BD and struct.unpack_from('<I', d, i)[0] & 0x8000]
    return list(zip(starts, starts[1:] + [text_end]))


def dead(exe, text_end):
    refs = references(exe)
    addrs = sorted(refs)
    import bisect
    res = []
    for a, z in functions(exe, text_end):
        k = bisect.bisect_left(addrs, a)
        if k >= len(addrs) or addrs[k] >= z:
            res.append((a, z - a))
    return res


def refs_into(exe, lo, hi):
    return [(a, r) for a, rs in sorted(references(exe).items()) if lo <= a < hi for r in rs]


if __name__ == '__main__':
    exe = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == 'refs':
        for a, r in refs_into(exe, int(sys.argv[3], 0), int(sys.argv[4], 0)):
            print(hex(a), r)
    else:
        te = {'B': 0x800A9000, 'R': 0x800A9800, 'N': 0x800B6000}[exe[0]]  # text end (before the VM opcode table etc.)
        for a, n in sorted(dead(exe, te), key=lambda x: -x[1])[:int(sys.argv[2]) if len(sys.argv) > 2 else 15]:
            print(hex(a), hex(n))
