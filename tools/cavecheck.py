"""Does any original game code reference the memory the patch caves occupy?

The caves (asm/main.asm: CAVE, CAVE2, CAVE3) are zero in the EXE image but are the game's BSS, so a game variable there
gets written at run time and corrupts our code or data. This scans the ORIGINAL executables and overlays of each book for
lui + load/store/addiu/ori pairs whose address lands in a cave (FAIL) or up to 0x10 before one (WARN: an array or struct
may be indexed into it). Static immediates only: indexed or pointer-walked use is not seen, so also run dsstate.py on real
play savestates.

  python -X utf8 tools/cavecheck.py          exit 1 on any FAIL
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

TREE = ROOT / 'work/orig/tree'
FILES = {'B': ['B_MAIN.EXE', 'B_EVENT.BIN', 'B_BATTLE.BIN'], 'R': ['R_MAIN.EXE', 'R_EVENT.BIN', 'R_BATTLE.BIN'],
         'N': ['N_MAIN.EXE', 'N_EVENT.BIN', 'N_BATTLE.BIN']}
MEM_OPS = (0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x28, 0x29, 0x2A, 0x2B, 0x2E)  # lb..swr
IMM_OPS = (0x08, 0x09, 0x0D)  # addi addiu ori
WRITES_RT = (0x08, 0x09, 0x0D, 0x0F, 0x20, 0x21, 0x23, 0x24, 0x25)
CAVE2_SPAN = 0x240  # 0x200 of tables + relocated strings (build.RELOCATE)


def caves(exe):
    """[(name, lo, hi)] of one main EXE: cave 1/2 (build.EXE_ADDR) and the text-tail pieces A/B/C (build/pieces.json);
    hi = end of the bytes actually used in build/files/<exe> (a game variable in the unused tail is harmless)."""
    import json
    import build
    a = build.EXE_ADDR[exe]
    out = [('CAVE', a['CAVE'], a['CAVE_END']), ('CAVE2', a['CAVE2'], a['CAVE2'] + CAVE2_SPAN)]
    pj = ROOT / 'build/pieces.json'
    if pj.exists():
        out += [('PIECE' + k, lo, hi) for k, (lo, hi) in sorted(json.loads(pj.read_text()).get(exe, {}).items())]
    built = ROOT / 'build/files' / exe
    if not built.exists():
        return out
    img = built.read_bytes()[0x800:]
    return [(n, lo, lo + len(img[lo - 0x80010000:hi - 0x80010000].rstrip(b'\0'))) for n, lo, hi in out]


def _sx(v):
    return v - 0x10000 if v & 0x8000 else v


def scan(path, cvs, base=0x80010000):
    """[(file offset of the lui, target address, cave name, 'FAIL'|'WARN')] without duplicates."""
    d = path.read_bytes()
    n = len(d) // 4
    out = {}
    for i in range(n):
        w = struct.unpack_from('<I', d, i * 4)[0]
        if w >> 26 != 0x0F:
            continue
        rt, hi = (w >> 16) & 31, w & 0xFFFF
        if hi < 0x8000:
            continue
        prev = w
        for j in range(i + 1, min(i + 12, n)):
            x = struct.unpack_from('<I', d, j * 4)[0]
            op, rs, rt2, imm = x >> 26, (x >> 21) & 31, (x >> 16) & 31, x & 0xFFFF
            if rs == rt and op in MEM_OPS + IMM_OPS:
                a = ((hi << 16) + (imm if op == 0x0D else _sx(imm))) & 0xFFFFFFFF
                for name, lo, hi_ in cvs:
                    if lo <= a < hi_:
                        out[(i * 4, a)] = (name, 'FAIL')
                    elif lo - 0x10 <= a < lo or hi_ <= a < hi_ + 0x10:
                        out.setdefault((i * 4, a), (name, 'WARN'))
            if op in WRITES_RT and rt2 == rt:
                break
            if j > i + 1 and (prev >> 26 in (2,) or prev & 0xFC1FFFFF == 8):  # after j / jr + delay slot: other path
                break
            prev = x
    return [(o, a, nm, lv) for (o, a), (nm, lv) in sorted(out.items())]


def scan_words(path, cvs, skip_own, base):
    """Pointers to a cave in the BUILT file's data (the build repoints strings, so the original tree is no guide).
    Words inside the caves themselves (our own code and tables) are skipped."""
    d = path.read_bytes()
    d = d[0x800:] if path.suffix == '.EXE' else d
    hits = []
    for i in range(0, len(d) - 3, 4):
        w = struct.unpack_from('<I', d, i)[0]
        if skip_own and any(lo <= base + i < hi for _, lo, hi in skip_own):
            continue
        for name, lo, hi in cvs:  # (cave 1/2 pointers are ours: the relocated Fire string, build.RELOCATE)
            if lo <= w < hi and name.startswith('PIECE'):
                hits.append((i, w, name, 'FAIL'))
    return hits


def check(verbose=True):
    """Returns the number of FAILs over all books; prints every hit."""
    fails = 0
    for book, files in FILES.items():
        cvs = caves(f'{book}_MAIN.EXE')
        for f in files:
            p = TREE / f
            if not p.exists():
                continue
            for off, a, name, lv in scan(p, cvs, 0x80010000 if f.endswith('.EXE') else 0x80170000):
                fails += lv == 'FAIL'
                if verbose and (lv == 'FAIL' or '-v' in sys.argv):  # WARNs (game vars next to a cave) only with -v
                    print(f'{lv} {f} +{off:#x} -> {a:#010x} ({name})')
            built = ROOT / 'build/files' / f
            if built.exists():
                for off, a, name, lv in scan_words(built, cvs, cvs if f.endswith('.EXE') else None,
                                                   0x80010000 if f.endswith('.EXE') else 0x80170000):
                    fails += 1
                    if verbose:
                        print(f'FAIL {f} (built) +{off:#x} points to {a:#010x} ({name})')
    return fails


if __name__ == '__main__':
    n = check()
    print(f'cavecheck: {n} references into the caves')
    sys.exit(1 if n else 0)
