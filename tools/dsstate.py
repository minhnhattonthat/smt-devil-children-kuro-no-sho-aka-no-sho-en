"""DuckStation savestate (.sav) reader: screenshot, RAM, and a check of our patched code/caves against the built EXE.

  python -X utf8 tools/dsstate.py check STATE...        diff RAM vs build/files/<book>_MAIN.EXE: code and the three caves
  python -X utf8 tools/dsstate.py dump STATE OUTDIR     OUTDIR/shot.png + OUTDIR/ram.bin (2 MiB, address - 0x80000000)

The user's states: C:/Users/Nathan/AppData/Local/DuckStation/savestates/SLPM-87040_N.sav. A state taken on an old build
or with a clobbered cave (the game writes its variables into BSS we mistook for free space, see cavecheck.py) shows here
as changed bytes in the caves / code, with the cave and address named. Needs the `zstandard` package.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

CODE_END = 0x800A9000  # EXE text ends before the event-VM opcode table (B_MAIN 0x800A9AA8); R/N similar


def load(path):
    """-> (RGBA screenshot (w, h, bytes), full machine memory blob of the state). The 14 header words sit at 168."""
    import zstandard
    d = Path(path).read_bytes()
    f = struct.unpack_from('<14I', d, 168)
    w, h, ssize, soff, dcomp, dsize, usize, doff = f[4], f[5], f[6], f[7], f[8], f[9], f[10], f[11]
    # 2 = zstd; the compressed screenshot comes first, the data follow it
    dec = zstandard.ZstdDecompressor()
    shot = dec.decompressobj().decompress(d[soff:soff + ssize])
    blob = dec.decompressobj().decompress(d[doff:doff + dsize])
    return (w, h, shot), blob


def ram_base(blob, exe):
    """Offset of RAM address 0x80000000 in the blob: find a stretch of the built EXE's text in it."""
    img = exe[0x800:]
    i = blob.find(img[0x1000:0x1040])
    return None if i < 0 else i - 0x11000


def runs(diffs, gap=16):
    out = []
    for i in diffs:
        if out and i - out[-1][1] <= gap:
            out[-1][1] = i
        else:
            out.append([i, i])
    return out


def check(path):
    import build
    import cavecheck
    (_, _, _), blob = load(path)
    best = None
    for name in build.EXE_ADDR:
        exe = (ROOT / 'build/files' / name).read_bytes()
        base = ram_base(blob, exe)
        if base is not None:
            best = (name, exe, base)
            break
    if not best:
        print(path, 'no built EXE matches this state (old build, or another game?)')
        return 1
    name, exe, base = best
    img = exe[0x800:]
    bad = 0
    print(f'{path}: {name}, RAM at blob +{base:#x}')
    cvs = {n: (lo, hi) for n, lo, hi in cavecheck.caves(name)}
    text = [i for i in range(0x1000, CODE_END - 0x80010000) if img[i] != blob[base + 0x10000 + i]]
    print('  code changed bytes:', len(text), [(hex(0x80010000 + a), hex(0x80010000 + z)) for a, z in runs(text)[:8]])
    bad += bool(text)
    for n, (lo, hi) in cvs.items():
        d = [i for i in range(lo - 0x80010000, hi - 0x80010000) if img[i] != blob[base + 0x10000 + i]]
        print(f'  {n} {lo:#x}-{hi:#x}: {len(d)} bytes changed', [(hex(0x80010000 + a), hex(0x80010000 + z)) for a, z in runs(d)[:8]])
        bad += bool(d)
    return bad


def main():
    cmd = sys.argv[1]
    if cmd == 'check':
        sys.exit(1 if sum(check(p) for p in sys.argv[2:]) else 0)
    if cmd == 'dump':
        (w, h, shot), blob = load(sys.argv[2])
        out = Path(sys.argv[3])
        out.mkdir(parents=True, exist_ok=True)
        from PIL import Image
        Image.frombytes('RGBA', (w, h), shot).save(out / 'shot.png')
        import build
        for name in build.EXE_ADDR:
            base = ram_base(blob, (ROOT / 'build/files' / name).read_bytes())
            if base is not None:
                (out / 'ram.bin').write_bytes(blob[base:base + 0x200000])
                print('ram.bin from', name)
                break


if __name__ == '__main__':
    main()
