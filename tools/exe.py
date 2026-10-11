"""EXE / overlay string map for B_MAIN, R_MAIN, N_MAIN (+ battle overlays later).

Strings are 16-bit text ending in FFFF. English replaces them in place (packed: 2 chars per halfword), so each
string gets a capacity in bytes: its own length plus zero padding up to the next 4-byte boundary, or the full field
for known fixed-size records (RECORDS).

  python -X utf8 tools/exe.py dump        write script/exe/NNN.json (never overwrites)
  python -X utf8 tools/exe.py stats
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TREE = ROOT / 'work' / 'orig' / 'tree'
EXES = (('BM', 'B_MAIN.EXE'), ('RM', 'R_MAIN.EXE'), ('NM', 'N_MAIN.EXE'))
BASE = 0x8000F800  # all three load at 0x80010000 (file offset 0x800)

# Fixed-size records, name at +0 in an 18-byte field (data from +18): (B_MAIN RAM base, stride, count).
# Bases are the expander's name tables (docs/re); other EXEs: found by matching B's first two records.
RECORDS = {
    'demon': (0x800C6030, 46, 277, 18),   # FFF8 / names
    'skill': (0x800C91C8, 30, 163, 18),   # FFF6
    'item': (0x800CA488, 26, 128, 18),    # FFF7
    'combo': (0x800BC780, 28, 128, 18),   # FFED
}
_B_MAIN = None

# Not text: name-entry character maps etc. (B_MAIN offsets; matched by JP content in other EXEs)
NOT_TEXT_PREFIX = ('vwxyz', '・…＝', 'eぁぅ', '・／：（？')


def record_slots(d):
    """{offset: field bytes} for every record name."""
    global _B_MAIN
    if _B_MAIN is None:
        _B_MAIN = (TREE / 'B_MAIN.EXE').read_bytes()
    out = {}
    for ram, stride, count, field in RECORDS.values():
        sig = _B_MAIN[ram - BASE: ram - BASE + 2 * stride]
        base = d.find(sig)
        assert base >= 0 and d.find(sig, base + 1) < 0, 'record table not unique: %X' % ram
        for i in range(count):
            out[base + i * stride] = field
    return out


def strings(d):
    """[(offset, length, capacity, jp)] for text strings in an EXE image."""
    rec = record_slots(d)
    in_rec = set()
    for off, field in rec.items():
        in_rec.update(range(off, off + field))
    found = {}
    for off, n, t in text.scan(d, minlen=2):
        if not in_rec.intersection(range(off, off + n)):  # stat bytes glued onto a record name
            found[off] = (n, t)
    for off in rec:
        t, n = text.decode(d, off)
        found[off] = (n, t)
    out = []
    offs = sorted(found)
    for i, off in enumerate(offs):
        n, t = found[off]
        if t.startswith(NOT_TEXT_PREFIX):
            continue
        if off in rec:
            cap = rec[off]
        else:
            cap = n
            nxt = offs[i + 1] if i + 1 < len(offs) else len(d)
            while (off + cap) % 4 and off + cap < nxt and d[off + cap] == 0:
                cap += 1
        out.append((off, n, cap, t))
    return out


def dump(chunk=120):
    dest = ROOT / 'script' / 'exe'
    dest.mkdir(parents=True, exist_ok=True)
    first, entries = {}, []
    for tag, name in EXES:
        d = (TREE / name).read_bytes()
        for off, n, cap, jp in strings(d):
            mid = '%s:%06X' % (tag, off)
            if jp in first:
                entries.append({'id': mid, 'same_as': first[jp]})
            else:
                first[jp] = mid
                entries.append({'id': mid, 'jp': jp, 'en': '', 'max': cap})
    files, cur, k = [], [], 0
    for e in entries:
        cur.append(e)
        k += 'jp' in e
        if k >= chunk:
            files.append(cur)
            cur, k = [], 0
    if cur:
        files.append(cur)
    wrote = 0
    for i, f in enumerate(files):
        p = dest / ('%03d.json' % i)
        if not p.exists():
            p.write_text(json.dumps(f, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
            wrote += 1
    print('%d entries, %d unique, %d files (%d written)' % (len(entries), len(first), len(files), wrote))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'stats'
    if cmd == 'dump':
        dump()
        return
    for tag, name in EXES:
        ss = strings((TREE / name).read_bytes())
        print(name, len(ss), 'strings', sum(s[1] for s in ss), 'bytes')


if __name__ == '__main__':
    main()
