"""Message id (as in the msgtour page names, 3000 + table index) -> script entry: python -X utf8 tools/debug/msgid.py 3408 4070
Prints the event JSON entry id, its Japanese and English text."""
import glob
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TABLE, BASE = 0x801BA0F8, 0x80170000


def entries():
    out = {}
    for f in glob.glob(str(ROOT / 'script/event/*.json')):
        for e in json.load(open(f, encoding='utf-8')):
            out[e['id']] = e
    return out


def lookup(ids, book='B'):
    d = (ROOT / 'work/orig/tree' / f'{book}_EVENT.BIN').read_bytes()
    ents = entries()
    for mid in ids:
        off = struct.unpack_from('<I', d, TABLE - BASE + 4 * (mid - 3000))[0] - BASE
        key = f'{book}:{off:X}'
        e = ents.get(key, {})
        if 'same_as' in e:
            e = ents.get(e['same_as'], e)
        yield mid, key, e.get('jp', '?'), e.get('en', '?')


if __name__ == '__main__':
    for mid, key, jp, en in lookup([int(a) for a in sys.argv[1:]]):
        print(f'{mid} {key}\n  JP {jp}\n  EN {en}')
