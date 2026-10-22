"""Build entry point.

  python -X utf8 build.py            build build/dc_en.bin + .cue from rom/ + translations
  python -X utf8 build.py dump       unpack the original disc to work/orig (once)
  python -X utf8 build.py identity   rebuild the untouched disc and compare SHA-1 with the original
  python -X utf8 build.py marker     every event message replaced by an [id] marker
"""
import hashlib
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROM_CUE = ROOT / 'rom' / 'Shin Megami Tensei - Devil Children - Kuro no Sho, Aka no Sho (Japan).cue'
ORIG = ROOT / 'work' / 'orig'
TREE = ORIG / 'tree'
BUILD = ROOT / 'build'
MKPSXISO = ROOT / 'tools' / 'mkpsxiso-2.30-win64'
ORIG_SHA1 = 'f7a3e476f595e656d5d5788a27aa6beec504a5bc'


def dump():
    if (ORIG / 'layout.xml').exists():
        return
    ORIG.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(MKPSXISO / 'dumpsxiso.exe'), '-x', str(TREE), '-s', str(ORIG / 'layout.xml'), str(ROM_CUE)],
                   check=True, capture_output=True)


def make_disc(overrides, out_bin):
    """overrides: disc file name -> path of replacement file. Unchanged files are read from work/orig/tree."""
    dump()
    xml = (ORIG / 'layout.xml').read_text(encoding='utf-8')

    def src(m):
        name = m[1]
        p = overrides.get(name.rstrip('.'), TREE / name.rstrip('.'))
        return '<file name="%s" source="%s"' % (name, Path(p).as_posix())
    xml = re.sub(r'<file name="([^"]+)"', src, xml)
    xml = xml.replace('file="tree/license_data.dat"', 'file="%s"' % (TREE / 'license_data.dat').as_posix())
    xml = xml.replace('source="tree"', 'source="%s"' % TREE.as_posix())
    out_bin = Path(out_bin)
    out_bin.parent.mkdir(parents=True, exist_ok=True)
    lay = out_bin.with_suffix('.xml')
    lay.write_text(xml, encoding='utf-8')
    r = subprocess.run([str(MKPSXISO / 'mkpsxiso.exe'), '-y', '-q', '-o', str(out_bin), '-c',
                        str(out_bin.with_suffix('.cue')), str(lay)], capture_output=True, text=True)
    if r.returncode:
        sys.exit('mkpsxiso failed:\n' + r.stdout + r.stderr)
    # mkpsxiso writes the bin's full path into the cue; make it relative so the pair can move
    cue = out_bin.with_suffix('.cue')
    cue.write_text(re.sub(r'FILE "[^"]*"', 'FILE "%s"' % out_bin.name, cue.read_text()), encoding='utf-8')


def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def identity():
    out = ROOT / 'work' / 'ident' / 'ident.bin'
    make_disc({}, out)
    ok = sha1(out) == ORIG_SHA1
    print('identity', 'OK' if ok else 'MISMATCH')
    return 0 if ok else 1


ARMIPS = ROOT / 'tools' / 'armips' / 'armips.exe'


MACCA = ('.#.....#', '.##...##', '.#.#.#.#', '.#..#..#', '#########', '.#.....#', '.#.....#')


def macca_mark():
    """Glyph 0x12 (the JP font's kana-like Macca sign, money displays): an M with a bar; body 1, shadow 3."""
    px = [[0] * 16 for _ in range(16)]
    for y, row in enumerate(MACCA):
        for x, c in enumerate(row):
            if c == '#':
                px[6 + y][1 + x] = 1
    for y in range(14, -1, -1):
        for x in range(14, -1, -1):
            if px[y][x] == 1 and px[y + 1][x + 1] == 0:
                px[y + 1][x + 1] = 3
    return px


def build_font(files):
    import font
    pac = bytearray((TREE / 'DEVIL.PAC').read_bytes())
    glyphs = font.load_en(ROOT / 'font' / 'en16.txt')
    widths = bytearray(256)
    for code, (px, adv) in glyphs.items():
        font.put_glyph(pac, code, px)
        widths[code - 0x100] = adv
    # the GPU samples one row past the 16-row cell: blank row 0 of the (kanji) cells under English glyphs
    for code in glyphs:
        below = code + 16
        if below not in glyphs and (below >> 8) == (code >> 8):
            blank = font.glyph(pac, below)
            blank[0] = [0] * 16
            font.put_glyph(pac, below, blank)
    font.put_glyph(pac, 0x12, macca_mark())
    import gfx
    gfx.apply(pac)  # book menu / title screen labels
    (files / 'DEVIL.PAC').write_bytes(pac)
    (BUILD / 'en_width.bin').write_bytes(widths)
    (BUILD / 'map8.bin').write_bytes(map8())
    (BUILD / 'name_tab.bin').write_bytes(name_tab())


NAME_PAGES = (  # name entry: 8 rows x (5 + gap + 5); shown with full-width glyphs, stored as English (asm name_map)
    ['ABCDE FGHIJ', 'KLMNO PQRST', 'UVWXY Z.!?-', '01234 56789', '+=/:# %()* '] + [' ' * 11] * 3,
    ['abcde fghij', 'klmno pqrst', 'uvwxy z.!?-', '01234 56789', '+=/:# %()* '] + [' ' * 11] * 3,
)
NAME_FW = {'.': '。', '!': '！', '?': '？', '-': '－', '+': '＋', '=': '＝', '/': '／',
           ':': '：', '#': '＃', '%': '％', '(': '（', ')': '）', '*': '※', ' ': '　'}


def name_tab():
    """JP glyph code (< 0x57) -> ASCII for name entry; inverse of the full-width grid glyphs."""
    import text
    m = bytearray(0x57)
    for row in NAME_PAGES[0] + NAME_PAGES[1]:
        for c in row:
            if c != ' ':
                m[text.JP_ENC[fw(c)]] = ord(c.upper())  # passwords are upper case (this table is only used there)
    return bytes(m)


def fw(c):
    """Full-width JP-table character for an ASCII name-grid character."""
    if c.isdigit():
        return chr(0xFF10 + int(c))
    return c if c.isalpha() else NAME_FW[c]


PASSWORDS = ('HOLYCHILDREN', 'MESSIAHDESCENDED', 'BEHEMOTH', 'LEVIATHAN', 'IKKAKUDRAGON', 'GABRIEL', 'METATRON')


def password_words(path):
    """Vine Center password screen: 7 answers (length table + 0x48-byte slots) become English, stored as
    0x100+ASCII like the typed units (asm name_map upper-cases what is typed)."""
    import text
    d = bytearray(path.read_bytes())
    tab = d.find(bytes([9, 8, 4, 6, 8, 5, 5, 0]))
    assert tab >= 0 and d.find(bytes([9, 8, 4, 6, 8, 5, 5, 0]), tab + 1) < 0
    assert d[tab + 12:tab + 12 + 4] == text.encode('ホー'), path
    for i, w in enumerate(PASSWORDS):
        d[tab + i] = len(w)
        at = tab + 12 + 0x48 * i
        d[at:at + 0x48] = b''.join(struct.pack('<H', 0x100 + ord(c)) for c in w).ljust(0x48, b'\0')
    path.write_bytes(d)


def name_grid(path):
    """Replace the two kana grids (hiragana / katakana pages) in a MAIN EXE with the Latin pages."""
    import text
    d = bytearray(path.read_bytes())
    for jp_first, page in (('あいうえお', NAME_PAGES[0]), ('アイウエオ', NAME_PAGES[1])):
        off = d.find(text.encode(jp_first + '　はひふへほ' if jp_first[0] == 'あ' else jp_first + '　ハヒフヘホ'))
        assert off >= 0, jp_first
        new = text.encode('{n}'.join(''.join(fw(c) for c in row) for row in page) + '{end}')
        old_len = text.decode(bytes(d), off)[1]
        assert len(new) == old_len, (len(new), old_len)
        d[off:off + old_len] = new
    path.write_bytes(d)


def map8():
    """ASCII -> 8x8 font code. The 8x8 font follows the JP table layout (A=0x23, a=0x3D, 0=0x19)."""
    import text
    m = bytearray(128)
    extra = {'.': '・', ',': '、', "'": '、', '"': '「', ':': '：', ';': '：', '!': '！', '?': '？', '-': '－',
             '+': '＋', '=': '＝', '%': '％', '#': '＃', '/': '／', '(': '（', ')': '）', '*': '※', '&': '＋',
             '[': '「', ']': '」'}
    for c in range(0x21, 0x7F):
        ch = chr(c)
        if ch.isalnum():
            m[c] = text.JP_ENC[ch if ch.isalpha() else chr(0xFF10 + int(ch))]
        elif ch in extra:
            m[c] = text.JP_ENC[extra[ch]]
    return bytes(m)


# The zero "caves" are the game's BSS. B 0x800D1BA4-0x800D1E40 (old cave 3) is a GTE command queue the game fills in
# battle: it overwrote our code (garbled glyphs, white screen). Cave 1/2 hold what has to stay there; the rest of the
# code lives in pieces A/B/C (asm/main.asm), the zero tails of translated text slots (place_pieces).
EXE_ADDR = {  # per-EXE hook addresses (same code, shifted)
    'B_MAIN.EXE': {'DRAW_HEAD': 0x80033B14, 'NUM_SITE': 0x80034728, 'CAVE': 0x800CF900, 'CAVE_END': 0x800CFBA0,
                   'CAVE2': 0x800D61FC, 'NAME_SEL': 0x80020EA0, 'NAME_DEF': 0x800212F4, 'EXP_X': 0x8001B7E0},
    'R_MAIN.EXE': {'DRAW_HEAD': 0x80033B0C, 'NUM_SITE': 0x80034720, 'CAVE': 0x800CFCC0, 'CAVE_END': 0x800CFF60,
                   'CAVE2': 0x800D65BC, 'NAME_SEL': 0x80020E94, 'NAME_DEF': 0x800212E8, 'EXP_X': 0x8001B808},
    'N_MAIN.EXE': {'DRAW_HEAD': 0x8004AF3C, 'NUM_SITE': 0x8004BB50, 'CAVE': 0x800DCC4C, 'CAVE_END': 0x800DCEEC,
                   'CAVE2': 0x800E3548, 'NAME_SEL': 0x8002214C, 'NAME_DEF': 0x800225A0, 'EXP_X': 0x8001CA8C},
}
PIECES = (('C', 0x150), ('B', 0x50), ('A', 0x40))  # largest first; asm checks the real sizes


def place_pieces(files, name):
    """{'A': (start, end), ...} RAM addresses of the zero tails (in the built image, nonzero in the original) that
    hold the asm pieces; the largest tail takes the largest piece. Also saved to build/pieces.json for cavecheck."""
    import json
    body = (files / name).read_bytes()[0x800:]
    orig = (ROOT / 'work/orig/tree' / name).read_bytes()[0x800:]
    runs, s = [], None
    for i in range(0x1000, min(len(body), 0xD0000) + 1):
        zero = i < len(body) and body[i] == 0
        if zero and s is None:
            s = i
        elif not zero and s is not None:
            # only the part up to the last original text byte: what follows may be original zero padding or BSS
            used = [k for k in range(s, i) if orig[k]]
            if used:
                a, z = (s + 3) & ~3, (used[-1] + 1) & ~3
                if z - a >= 0x40:
                    runs.append((z - a, a, z))
            s = None
    runs.sort(reverse=True)
    out = {}
    for (key, size), (n, a, z) in zip(PIECES, runs):
        if n < size:
            sys.exit(f'{name}: no free text tail of {size:#x} bytes for piece {key} (largest {n:#x})')
        out[key] = (0x80010000 + a, 0x80010000 + z)
    if len(out) < len(PIECES):
        sys.exit(f'{name}: only {len(runs)} free text tails for {len(PIECES)} pieces')
    path = BUILD / 'pieces.json'
    allp = json.loads(path.read_text()) if path.exists() else {}
    allp[name] = out
    path.write_text(json.dumps(allp))
    return out


EXE_TAG = {'B_MAIN.EXE': 'BM', 'R_MAIN.EXE': 'RM', 'N_MAIN.EXE': 'NM', 'B_BATTLE.BIN': 'BB', 'R_BATTLE.BIN': 'RB',
           'B_EVENT.BIN': 'BE', 'R_EVENT.BIN': 'RE'}


def exe_marker(mid, jp, cap):
    """Offset tag that fits the string's capacity, keeping its {codes} (EXE marker build)."""
    import text
    tag = mid.split(':')[1].lstrip('0') or '0'
    codes = ''.join(re.findall(r'\{[^}]*\}', jp.replace('{end}', '')))
    for n in range(len(tag), 0, -1):
        s = codes + tag[-n:] + '{end}'
        if len(text.encode_en(s)) <= cap:
            return s
    return jp


# Strings that outgrow their slot move to spare bytes at the end of cave 2 (after the data tables) and their
# pointer slot is repointed: {EXE: {string offset: [pointer slot file offsets]}}. The element/race/status names
# live in one pointer table (file 0x960); Fire (ヒ) has only a 4-byte slot.
RELOCATE = {'B_MAIN.EXE': {0xB074C: [0x990, 0x5A54]}, 'R_MAIN.EXE': {0xB0AE0: [0x990, 0x5A88]},
            'N_MAIN.EXE': {0xBC190: [0x990, 0x4F88]}}
CAVE2_USED = 476  # bytes used by asm/main.asm in cave 2 (pk_pend 4 + widths 256 + map8 128 + name_tab 87, aligned)


def insert_strings(files, name, mode, sub, extract, src=None):
    """In-place packed English for EXE/overlay strings (script/<sub>); writes build/files/<name>.
    src: bytes to patch instead of the original file (an event overlay after its message repack)."""
    import lint
    import text
    d = bytearray(src or (TREE / name).read_bytes())
    tl = load_script(sub)
    tag = EXE_TAG[name]
    jp_first = exe_first_ids(sub)
    pool = None
    if sub == 'exe':
        import exe
        pool = exe.label_pool(bytes(d))
    pooled = {}
    moved = []
    for off, ln, cap, jp in extract(bytes(d)):
        mid = '%s:%06X' % (tag, off)
        if mode == 'marker':
            en = exe_marker(mid, jp, cap)
        else:
            en = tl.get(jp_first.get(jp, mid), '')
        if pool and pool[2] <= off < pool[3]:
            pooled[off] = en if en and en != jp else None
            continue
        if not en or en == jp:
            continue
        if '{wait}' in jp and mode != 'marker':
            en = lint.prepare(jp, en)  # dialogue text: wrap like events
        b = text.encode_en(en)
        if len(b) > cap:
            slots = RELOCATE.get(name, {}).get(off) if sub == 'exe' else None
            if not slots:
                sys.exit('%s %s: %d bytes > %d' % (name, mid, len(b), cap))
            used = CAVE2_USED + sum(len(x[0]) for x in moved)
            if used + len(b) > 512:
                sys.exit('%s: cave 2 spare overflow' % name)
            moved.append((b, EXE_ADDR[name]['CAVE2'] - 0x8000F800 + used, slots))
            continue
        d[off:off + cap] = b + bytes(cap - len(b))
    for b, at, slots in moved:
        d[at:at + len(b)] = b
        for slot in slots:
            struct.pack_into('<I', d, slot, 0x8000F800 + at)
    if pool:
        repack_labels(d, pool, pooled, name)
    (files / name).write_bytes(d)


def repack_labels(d, pool, pooled, name):
    """Speaker labels: pack every label (English or original) into the pool, repoint the label table."""
    import text
    tab, slots, start, end = pool
    orig = bytes(d)
    placed, cur = {}, start
    for slot, target in slots:
        if target not in placed:
            en = pooled.get(target)
            b = text.encode_en(en) if en else orig[target:target + text.decode(orig, target)[1]]
            placed[target] = (cur, b)
            cur += len(b)
            if cur > end:
                sys.exit('%s: speaker labels overflow the pool (%d > %d bytes)' % (name, cur - start, end - start))
    d[start:end] = bytes(end - start)
    for target, (at, b) in placed.items():
        d[at:at + len(b)] = b
    for slot, target in slots:
        struct.pack_into('<I', d, slot, 0x8000F800 + placed[target][0])


def build_exe(files, name, mode='normal'):
    import exe
    insert_strings(files, name, mode, 'exe', exe.strings)
    name_grid(files / name)
    password_words(files / name)
    eq = [x for k, v in EXE_ADDR[name].items() for x in ('-equ', k, '0x%X' % v)]
    for key, (a, z) in place_pieces(files, name).items():
        eq += ['-equ', f'CAVE{key}', '0x%X' % a, '-equ', f'CAVE{key}_END', '0x%X' % z]
    r = subprocess.run([str(ARMIPS), str(ROOT / 'asm' / 'main.asm'), '-strequ', 'EXE', str(files / name),
                        '-strequ', 'WIDTHS', str(BUILD / 'en_width.bin'), '-strequ', 'MAP8_FILE', str(BUILD / 'map8.bin'),
                        '-strequ', 'NAME_TAB_FILE', str(BUILD / 'name_tab.bin')] + eq, capture_output=True, text=True)
    if r.returncode:
        sys.exit('armips failed:\n' + r.stdout + r.stderr)


def exe_first_ids(sub='exe'):
    """JP text -> id of the entry that carries its English (script/exe dedupes identical JP across EXEs)."""
    import json
    out = {}
    for p in sorted((ROOT / 'script' / sub).glob('*.json')):
        for e in json.loads(p.read_text(encoding='utf-8')):
            if 'jp' in e:
                out.setdefault(e['jp'], e['id'])
    return out


def load_script(sub):
    """id -> English (same_as resolved; '' = untranslated) for script/<sub>/*.json."""
    import json
    raw = {}
    for p in sorted((ROOT / 'script' / sub).glob('*.json')):
        for e in json.loads(p.read_text(encoding='utf-8')):
            raw[e['id']] = e
    out = {}
    for k, e in raw.items():
        while 'same_as' in e:
            e = raw[e['same_as']]
        out[k] = e.get('en', '')
    return out


def marker_text(mid, jp):
    """Keep every control code; each glyph run becomes filler ~1.7x its JP length (realistic English size),
    the first run starting with the id tag."""
    filler = 'The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. ' * 4
    parts = re.split(r'(\{[^}]*\}|\[[0-9A-F]{4}\])', jp)
    first = True
    out = []
    for p in parts:
        if not p or p[0] in '{[':
            out.append(p)
            continue
        n = max(4, int(len(p) * 1.7))
        if first:
            tag = '[%s] ' % mid.replace(':', '')
            out.append((tag + filler)[:max(n, len(tag) + 4)])
            first = False
        else:
            out.append(filler[:n])
    return ''.join(out)


def build_event(files, tag, name, mode):
    import events
    import lint
    import text
    d = (TREE / name).read_bytes()
    msgs = events.messages(d)
    tl = load_script('event')
    new = {}
    for off, (n, _) in msgs.items():
        mid = '%s:%05X' % (tag, off)
        if mode == 'marker':
            new[off] = text.encode_en(marker_text(mid, text.decode(d, off)[0]))
        elif tl.get(mid):
            new[off] = text.encode_en(lint.prepare(text.decode(d, off)[0], tl[mid]))
        else:
            new[off] = d[off:off + n]
    out, st = events.repack(d, msgs, new)
    import exe
    insert_strings(files, name, mode, 'battle', exe.event_strings, src=bytes(out))  # code-addressed strings
    print('%s: %d/%d bytes (%.0f%%)' % (name, st['used'], st['capacity'], 100 * st['used'] / st['capacity']))


def build(mode='normal'):
    sys.path.insert(0, str(ROOT / 'tools'))
    files = BUILD / 'files'
    if files.exists():
        shutil.rmtree(files)
    files.mkdir(parents=True)
    build_font(files)
    for exe in EXE_ADDR:
        build_exe(files, exe, mode)
    import exe as exe_mod
    for ov in ('B_BATTLE.BIN', 'R_BATTLE.BIN'):
        insert_strings(files, ov, mode, 'battle', exe_mod.battle_strings)
    build_event(files, 'B', 'B_EVENT.BIN', mode)
    build_event(files, 'R', 'R_EVENT.BIN', mode)
    import cavecheck
    if cavecheck.check():  # the game's own variables sit in a cave: see tools/cavecheck.py
        sys.exit('build stopped: game code references the patch caves')
    overrides = {p.name: p for p in files.iterdir()}
    make_disc(overrides, BUILD / 'dc_en.bin')
    print('built', BUILD / 'dc_en.bin')
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    sys.path.insert(0, str(ROOT / 'tools'))
    import check_rom
    check_rom.check()
    sys.exit({'dump': lambda: dump() or 0, 'identity': identity, 'build': build,
              'marker': lambda: build('marker')}[cmd]())
