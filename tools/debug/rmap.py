"""Map a B_MAIN function address to the same function in R_MAIN (R shifts code by a different amount per function).
  python -X utf8 tools/debug/rmap.py 0x800262F4 0x800523A8 ...
Matches the first 24 instructions with call targets and immediates masked; prints the R address or '?'."""
import struct
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x80010000 - 0x800
WORDS = 24
IMM_OPS = {0x09, 0x0D, 0x0F, 0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B}  # addiu ori lui lb lh lw lbu lhu sb sh sw


def mask(w):
    op = w >> 26
    if op in (2, 3):
        return w & 0xFC000000
    if op in IMM_OPS:
        return w & 0xFFFF0000
    return w


@lru_cache(None)
def load(name):
    d = (ROOT / 'work/orig/tree' / name).read_bytes()
    return d, [struct.unpack_from('<I', d, o)[0] for o in range(0, len(d) - 3, 4)]


def rmap(addr, src='B_MAIN.EXE', dst='R_MAIN.EXE'):
    d, w = load(src)
    i = (addr - BASE) // 4
    pat = [mask(x) for x in w[i:i + WORDS]]
    _, rw = load(dst)
    hits = [j for j in range(len(rw) - WORDS) if [mask(x) for x in rw[j:j + WORDS]] == pat]
    return [BASE + 4 * j for j in hits]


if __name__ == '__main__':
    for a in sys.argv[1:]:
        r = rmap(int(a, 0))
        print(a, ' '.join('%08X' % x for x in r) if r else '?')
