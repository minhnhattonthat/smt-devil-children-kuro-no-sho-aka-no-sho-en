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

# Strings the kana-ratio scan misses (Latin / digits / symbols dominate): found by their JP opening, in any file.
FORCED_JP = ('EXP：', '{name}のHPが', 'メダルを何枚かけますか', '負け・・・', 'Pダウンコンボ', 'Pアップコンボ',
             '{face:0002}なんか、めんどくさくなっちゃった', 'なぞのデビル{end}', '回復　　{end}',
             'はい{end}')  # the Yes of the nickname Yes/No box (the scan took only the いいえ next to it)


def forced(d):
    """{offset: (bytes, text)} of FORCED_JP strings in d that end in {end}."""
    out = {}
    for s in FORCED_JP:
        sig = text.encode(s)
        i = d.find(sig)
        while i >= 0:
            if i % 2 == 0:
                t, n = text.decode(d, i)
                if t.endswith('{end}'):
                    out[i] = (n, t)
            i = d.find(sig, i + 1)
    return out


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


def referenced(d, base=BASE):
    """Offsets referenced by an aligned 32-bit pointer or a lui + addiu/ori pair (within 16 instructions)."""
    out = set()
    end = base + len(d)
    regs = {}
    for o in range(0, len(d) - 3, 4):
        w = struct.unpack_from('<I', d, o)[0]
        if base <= w < end and not w & 1:
            out.add(w - base)
        op = w >> 26
        if op == 0x0F:
            regs[(w >> 16) & 31] = ((w & 0xFFFF) << 16, o)
        elif op in (0x09, 0x0D) and (w >> 21) & 31 in regs:
            hi, ho = regs[(w >> 21) & 31]
            lo = w & 0xFFFF
            if op == 0x09 and lo & 0x8000:
                lo -= 0x10000
            v = (hi + lo) & 0xFFFFFFFF
            if o - ho <= 64 and base <= v < end and not v & 1:
                out.add(v - base)
    return out


def strings(d, records=True, base=BASE):
    """[(offset, length, capacity, jp)] for text strings in an EXE image."""
    rec = record_slots(d) if records else {}
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
    for off, (n, t) in forced(d).items():
        for o in [o for o, (m, _) in found.items() if o < off < o + m]:  # a run that swallowed its leading junk
            del found[o]
        found[off] = (n, t)
    covered = set()
    ends = set()
    for off, (n, _) in found.items():
        covered.update(range(off, off + n))
        ends.add(off + n)
    extra = {}  # end offset -> (start, n, text): kanji-only strings the kana-ratio scan misses (e.g. 回復)
    for off in referenced(d, base):
        if off in covered or off in found:
            continue
        t, n = text.decode(d, off)
        if off + n in ends:  # same string seen from its leading space / a shared tail
            continue
        units = [struct.unpack_from('<H', d, p)[0] for p in range(off, off + n - 2, 2)]
        if t.endswith('{end}') and n <= 256 and units and all(u < text.NGLYPH or u in text.CTRL for u in units) \
                and any(0x57 <= u < text.NGLYPH for u in units):
            if off + n not in extra or off > extra[off + n][0]:  # shared tail: keep the shortest
                extra[off + n] = (off, n, t)
    for off, n, t in extra.values():
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


LABEL_TABLE_B = 0x800BE2D4   # speaker-label pointers (face id -> name), B_MAIN
LABEL_COUNT = 0x6A           # entries past this are unrelated pointer data (docs/names.md)


def label_pool(d):
    """(table offset, [(slot offset, string offset)], pool start, pool end) for the speaker-label table.

    The label strings are referenced only through this table, so the build may repack them anywhere inside
    [start, end) and repoint the slots."""
    global _B_MAIN
    if _B_MAIN is None:
        _B_MAIN = (TREE / 'B_MAIN.EXE').read_bytes()
    bt = LABEL_TABLE_B - BASE
    btarg = [struct.unpack_from('<I', _B_MAIN, bt + 4 * i)[0] - BASE for i in range(LABEL_COUNT)]
    bstart = min(btarg)
    bend = max(t + text.decode(_B_MAIN, t)[1] for t in btarg)
    sig = _B_MAIN[bstart:bend]
    start = d.find(sig)
    assert start >= 0, 'label pool not found'
    delta = start - bstart
    want = [t + delta + BASE for t in btarg]
    raw = b''.join(struct.pack('<I', w) for w in want)
    tab = d.find(raw)
    assert tab >= 0 and tab % 4 == 0, 'label table not found'
    slots = [(tab + 4 * i, want[i] - BASE) for i in range(LABEL_COUNT)]
    end = bend + delta
    while end % 4:
        end += 1
    return tab, slots, start, end


BATTLES = (('BB', 'B_BATTLE.BIN'), ('RB', 'R_BATTLE.BIN'))  # overlays at 0x80170000, no record tables known


def battle_strings(d):
    """Battle overlays hold many data runs that decode as kana: keep real-looking text only."""
    out = []
    force = forced(d)
    for off, n, cap, jp in strings(d, records=False, base=0x80170000):
        if off in force:
            out.append((off, n, cap, jp))
            continue
        units = [struct.unpack_from('<H', d, p)[0] for p in range(off, off + n - 2, 2)]
        glyphs = [u for u in units if u < text.NGLYPH]
        spaced = sum(1 for u in glyphs if u == 0) * 2 >= len(glyphs)  # 'ご　さ　ざ' kana tables
        latin = any(0x23 <= u <= 0x56 for u in glyphs)
        escapes = any(u >= text.NGLYPH and u not in text.CTRL for u in units) or 0xFE in glyphs or 0xFF in glyphs
        punct_start = bool(glyphs) and units[0] == glyphs[0] and 0 < glyphs[0] <= 0x18  # '。モ', '・ホペ'
        if punct_start:
            continue
        if '{wait}' in jp or '{face:' in jp or (len(glyphs) >= 2 and not spaced and not latin and not escapes):
            out.append((off, n, cap, jp))
    return out


def dump(chunk=120, sub='exe', files=EXES, extract=None):
    dest = ROOT / 'script' / sub
    dest.mkdir(parents=True, exist_ok=True)
    first, entries = {}, []
    for tag, name in files:
        d = (TREE / name).read_bytes()
        for off, n, cap, jp in (extract or strings)(d):
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


def append(chunk=120, sub='exe', exes=EXES, extract=None):
    dest = ROOT / 'script' / sub
    first, have = {}, set()
    files = sorted(dest.glob('*.json'))
    for p in files:
        for e in json.loads(p.read_text(encoding='utf-8')):
            have.add(e['id'])
            if 'jp' in e:
                first.setdefault(e['jp'], e['id'])
    entries = []
    for tag, name in exes:
        d = (TREE / name).read_bytes()
        for off, n, cap, jp in (extract or strings)(d):
            mid = '%s:%06X' % (tag, off)
            if mid in have:
                continue
            if jp in first:
                entries.append({'id': mid, 'same_as': first[jp]})
            else:
                first[jp] = mid
                entries.append({'id': mid, 'jp': jp, 'en': '', 'max': cap})
    num = int(files[-1].stem) + 1 if files else 0
    for i in range(0, len(entries), chunk):
        p = dest / ('%03d.json' % num)
        p.write_text(json.dumps(entries[i:i + chunk], ensure_ascii=False, indent=1) + '\n', encoding='utf-8',
                     newline='\n')
        num += 1
    print('appended', len(entries), 'entries')


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'stats'
    if cmd == 'dump':
        dump()
        return
    if cmd == 'append':  # strings found since the first dump -> new script/exe files (existing ones untouched)
        append()
        return
    if cmd == 'append-battle':
        append(sub='battle', exes=BATTLES, extract=battle_strings)
        return
    if cmd == 'dump-battle':
        dump(sub='battle', files=BATTLES, extract=battle_strings)
        return
    for tag, name in EXES:
        ss = strings((TREE / name).read_bytes())
        print(name, len(ss), 'strings', sum(s[1] for s in ss), 'bytes')


if __name__ == '__main__':
    main()
