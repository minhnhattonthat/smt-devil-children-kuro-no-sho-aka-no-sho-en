"""Dump event messages to script/event/NNN.json (never overwrites an existing file).

Ids are "B:XXXXX" / "R:XXXXX" (file offset in B_EVENT/R_EVENT.BIN). Messages whose JP text repeats an earlier one
(B first, then R) are listed as {"id", "same_as"} only; the build reuses the first one's English.

  python -X utf8 tools/extract.py events [--chunk 80]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import events  # noqa: E402
import text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TREE = ROOT / 'work' / 'orig' / 'tree'
EVENT_FILES = (('B', 'B_EVENT.BIN'), ('R', 'R_EVENT.BIN'))


def event_entries():
    """All event messages in disc order: list of dicts (id, jp, same_as?)."""
    first = {}
    out = []
    for tag, name in EVENT_FILES:
        d = (TREE / name).read_bytes()
        for off in sorted(events.messages(d)):
            jp = text.decode(d, off)[0]
            mid = '%s:%05X' % (tag, off)
            if jp in first:
                out.append({'id': mid, 'same_as': first[jp]})
            else:
                first[jp] = mid
                out.append({'id': mid, 'jp': jp, 'en': ''})
    return out


def dump_events(chunk):
    dest = ROOT / 'script' / 'event'
    dest.mkdir(parents=True, exist_ok=True)
    entries = event_entries()
    files, cur, n = [], [], 0
    for e in entries:
        cur.append(e)
        n += 'jp' in e
        if n >= chunk:
            files.append(cur)
            cur, n = [], 0
    if cur:
        files.append(cur)
    wrote = 0
    for i, f in enumerate(files):
        p = dest / ('%03d.json' % i)
        if p.exists():
            continue
        p.write_text(json.dumps(f, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
        wrote += 1
    print('%d entries, %d unique, %d files (%d written)' % (len(entries), sum('jp' in e for e in entries),
                                                          len(files), wrote))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('what', choices=['events'])
    ap.add_argument('--chunk', type=int, default=80)
    a = ap.parse_args()
    dump_events(a.chunk)


if __name__ == '__main__':
    main()
