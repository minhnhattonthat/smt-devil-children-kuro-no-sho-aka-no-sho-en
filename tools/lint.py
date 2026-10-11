"""English text checks and auto-wrap for event messages.

Translators write each box (page) as running text; wrap() breaks it into lines with {n} using the VWF widths.
lint_event(jp, en) returns a list of error strings ([] = ok).

  python -X utf8 tools/lint.py "text" [--box dialog]     width per wrapped line (dry-run fitter)
  python -X utf8 tools/lint.py --all                     lint every translated script entry
"""
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

# dialogue window: text x=16..240 (measured in-game); 3 rows but row 1 holds the speaker label when a portrait
# is shown, so pages get 2 lines. Choice windows: options are JP lines indented with a full-width space.
BOX = {'dialog': {'px': 224, 'lines': 2}, 'choice': {'px': 200, 'lines': 6}}
CURSOR = '[0000]'  # full-width space glyph (12 px) the choice cursor sits in
MAX_UNITS = 250       # window source buffer: byte index -> 255 halfwords incl. inserted names
NAME_UNITS = {'name': 8, 'partner': 12, 'ed': 12, 'f5': 12, 'f6': 12, 'f7': 12}  # estimated inserted name lengths
TOKEN = re.compile(r'(\{[^}]*\}|\[[0-9A-F]{4}\])')
BREAKS = ('page', 'f0')  # codes that start a new box (f0: assumed to clear; see docs/re)


@lru_cache(None)
def widths():
    import font
    return {c - font.EN_BASE: adv for c, (px, adv) in font.load_en(ROOT / 'font' / 'en16.txt').items()}


def text_width(s):
    """Pixel width of plain text; a [0000] cursor escape counts 12 px."""
    w = widths()
    return 12 * s.count(CURSOR) + sum(w.get(ord(c), 16) for c in s.replace(CURSOR, ''))


def wrap_page(s, px):
    """Greedy wrap of one page's plain text (codes kept inline, zero width) -> list of lines."""
    words = re.split(r'( )', s)
    lines, cur = [], ''
    for i in range(0, len(words), 2):
        word = words[i]
        cand = (cur + ' ' + word) if cur else word
        if cur and text_width(TOKEN.sub('', cand)) > px:
            lines.append(cur)
            cur = word
        else:
            cur = cand
    lines.append(cur)
    return lines


def balance(lines, px):
    """Even out line lengths for 2+ line pages without increasing the line count (avoids one-word widows)."""
    if len(lines) < 2:
        return lines
    words = ' '.join(lines).split(' ')
    best = lines
    target = len(lines)
    lo, hi = 1, px
    while lo < hi:  # smallest width that still wraps into `target` lines
        mid = (lo + hi) // 2
        if len(wrap_page(' '.join(words), mid)) <= target:
            hi = mid
        else:
            lo = mid + 1
    cand = wrap_page(' '.join(words), lo)
    if len(cand) == target:
        best = cand
    return best


def wrap(en, box='dialog'):
    """Insert {n} so every page fits the box width. Explicit {n} in the input is kept as a hard break."""
    px = BOX[box]['px']
    out = []
    # split into pages on page-break codes, keep codes
    parts = re.split(r'(\{(?:%s)\})' % '|'.join(BREAKS), en)
    for p in parts:
        if re.fullmatch(r'\{(?:%s)\}' % '|'.join(BREAKS), p or ''):
            out.append(p)
            continue
        lines = []
        for hard in p.split('{n}'):
            lines += balance(wrap_page(hard, px), px)
        out.append('{n}'.join(lines))
    return ''.join(out)


def pages(wrapped):
    return [pg.split('{n}') for pg in re.split(r'\{(?:%s)\}' % '|'.join(BREAKS), wrapped)]


def codes(s):
    """Control codes that must survive translation ([XXXX] glyph escapes are free text, e.g. record data)."""
    return [t for t in TOKEN.findall(s) if t != '{n}' and t[0] == '{']


def units(wrapped):
    """Halfwords the window buffer holds: packed text = 2 chars per unit, codes 1 + args, names inserted."""
    n = 0
    for t in TOKEN.split(wrapped):
        if not t:
            continue
        if t[0] in '{[':
            name = t[1:].split(':')[0].rstrip('}')
            n += 1 + t.count(':') + NAME_UNITS.get(name, 0)
        else:
            n += (len(t) + 1) // 2
    return n


@lru_cache(None)
def avoid_terms():
    """Avoid-column spellings from glossary.md tables."""
    out = []
    for line in (ROOT / 'glossary.md').read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if line.startswith('|') and len(cells) >= 4 and cells[0] not in ('JP', '---'):
            for a in re.split(r',\s*', cells[-1]):
                if a and not set(a) <= set('-'):
                    out.append(a)
    return out


def form(jp):
    """'choice' for option menus (no {wait}, every line starts with a full-width space), else 'dialog'."""
    lines = TOKEN.sub(lambda m: '' if m[0] != '{n}' else m[0], jp).replace('{end}', '').split('{n}')
    if '{wait}' not in jp and len(lines) >= 2 and all(ln.startswith('　') for ln in lines):
        return 'choice'
    return 'dialog'


def prepare(jp, en):
    """English as it goes into the build: dialogue auto-wrapped; choices get the cursor indent per option."""
    if form(jp) == 'choice':
        return '{n}'.join(ln if ln.startswith(CURSOR) else CURSOR + ln.lstrip(' ') for ln in en.split('{n}'))
    # {f0} scrolls the box up one line (seen in-game); as a page break English never overflows after it
    return wrap(en.replace('{f0}', '{page}'), 'dialog')


@lru_cache(None)
def allowed_long():
    """Ids allowed more lines per page (e.g. overlapping pointers into one JP message): tools/lint_allow.txt."""
    p = Path(__file__).with_name('lint_allow.txt')
    return frozenset(ln.split()[0] for ln in p.read_text(encoding='utf-8').splitlines()
                     if ln.strip() and not ln.startswith('#')) if p.exists() else frozenset()


def lint_event(jp, en, box=None, mid=None):
    box = box or form(jp)
    errs = []
    if box == 'choice' and en.count('{n}') != jp.count('{n}'):
        errs.append('choice: keep one option per line ({n} count %d, JP has %d)' % (en.count('{n}'),
                                                                               jp.count('{n}')))
    if not en.endswith('{end}'):
        errs.append('must end with {end}')
    bad = [c for c in TOKEN.sub('', en) if not 0x20 <= ord(c) < 0x7F]
    if bad:
        errs.append('non-ASCII: %r' % ''.join(sorted(set(bad))))
    if codes(jp) != codes(en):
        errs.append('control codes differ: jp %s / en %s' % (''.join(codes(jp)), ''.join(codes(en))))
    w = prepare(jp, en)
    for i, pg in enumerate(pages(w)):
        text_lines = [TOKEN.sub('', ln) for ln in pg]
        if len(pg) > BOX[box]['lines'] and mid not in allowed_long():
            errs.append('page %d: %d lines > %d (split the box or shorten)' % (i + 1, len(pg), BOX[box]['lines']))
        for ln in text_lines:
            if text_width(ln) > BOX[box]['px']:
                errs.append('line too wide (%dpx): %s' % (text_width(ln), ln))
    u = units(w)
    if u > MAX_UNITS:
        errs.append('message too long: %d units > %d' % (u, MAX_UNITS))
    for a in avoid_terms():
        if re.search(r'\b%s\b' % re.escape(a), TOKEN.sub('', en)):
            errs.append('glossary: avoid "%s"' % a)
    if re.search(r'\{\w+\}(st|nd|rd|th)\b', en):
        errs.append('ordinal suffix glued to a variable')
    return errs


def jp_line_px(jp):
    """Widest JP line in px (12 px per glyph) - the space the UI gave the original."""
    lines = TOKEN.sub(lambda m: m[0] if m[0] == '{n}' else '', jp).split('{n}')
    return max(12 * len(ln) for ln in lines)


EXE_MIN_PX = 60  # short labels: allow English a little wider than tiny JP labels (QA confirms per screen)


def lint_exe(jp, en, cap, px=None):
    """EXE/overlay strings: in-place, so the packed size must fit `cap` bytes; lines no wider than the JP's."""
    import text
    if en == jp:  # data / debug string left as is
        return []
    if '{wait}' in jp:  # dialogue window text inside the EXE: event rules, plus the in-place size
        errs = lint_event(jp, en)
        if not any('non-ASCII' in e for e in errs):
            size = len(text.encode_en(prepare(jp, en)))
            if size > cap:
                errs.append('too long: %d bytes > %d' % (size, cap))
        return errs
    errs = []
    if not en.endswith('{end}'):
        errs.append('must end with {end}')
    bad = [c for c in TOKEN.sub('', en) if not 0x20 <= ord(c) < 0x7F]
    if bad:
        errs.append('non-ASCII: %r' % ''.join(sorted(set(bad))))
    if codes(jp) != codes(en):
        errs.append('control codes differ: jp %s / en %s' % (''.join(codes(jp)), ''.join(codes(en))))
    if en.count('{n}') > jp.count('{n}'):
        errs.append('more lines than JP (%d > %d)' % (en.count('{n}') + 1, jp.count('{n}') + 1))
    if not bad:
        size = len(text.encode_en(en))
        if size > cap:
            errs.append('too long: %d bytes > %d (about %d chars max)' % (size, cap, cap - 2))
    limit = px or max(jp_line_px(jp), EXE_MIN_PX)
    for ln in TOKEN.sub(lambda m: m[0] if m[0] == '{n}' else '', en).split('{n}'):
        if text_width(ln) > limit:
            errs.append('line %dpx > %dpx: %s' % (text_width(ln), limit, ln))
    for a in avoid_terms():
        if re.search(r'\b%s\b' % re.escape(a), TOKEN.sub('', en)):
            errs.append('glossary: avoid "%s"' % a)
    return errs


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('text', nargs='?')
    ap.add_argument('--box', default='dialog')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    if a.text:
        for pg in pages(wrap(a.text, a.box)):
            for ln in pg:
                t = TOKEN.sub('', ln)
                print('%4dpx  %s' % (text_width(t), t))
            print('--')
        return 0
    bad = n = 0
    for sub in ('exe', 'battle'):
        for p in sorted((ROOT / 'script' / sub).glob('*.json')):
            for e in json.loads(p.read_text(encoding='utf-8')):
                if e.get('en') and e['en'] != e['jp']:
                    n += 1
                    for err in lint_exe(e['jp'], e['en'], e['max'], e.get('px')):
                        bad += 1
                        print('%s/%s %s: %s' % (sub, p.name, e['id'], err))
    for p in sorted((ROOT / 'script' / 'event').glob('*.json')):
        for e in json.loads(p.read_text(encoding='utf-8')):
            if e.get('en'):
                n += 1
                for err in lint_event(e['jp'], e['en'], mid=e['id']):
                    bad += 1
                    print('%s %s: %s' % (p.name, e['id'], err))
    print('lint: %d translated, %d errors' % (n, bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
