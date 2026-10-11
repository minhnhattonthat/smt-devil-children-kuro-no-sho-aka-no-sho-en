"""Translation batches for event messages (script/event/NNN.json <-> work/tl/eNNN.tsv).

  python -X utf8 tools/batches.py split [NNN ...]   write work/tl/eNNN.tsv (+ build/terms_eNNN.txt) for untranslated
  python -X utf8 tools/batches.py check eNNN         validate work/tl/eNNN.out.tsv (prints OK or errors)
  python -X utf8 tools/batches.py merge eNNN         check, then write the English into script/event/NNN.json

Input TSV:  id <TAB> speaker <TAB> Japanese   (codes inline; see docs/translator-brief.md)
Output TSV: id <TAB> English
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
import lint  # noqa: E402

TL = ROOT / 'work' / 'tl'
EV = ROOT / 'script' / 'event'


def faces():
    """{(book, face): name} from docs/faces.md table rows: | face | book(s) | JP | English | ..."""
    out = {}
    p = ROOT / 'docs' / 'faces.md'
    if not p.exists():
        return out
    for line in p.read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 4 or not re.fullmatch(r'[0-9A-Fa-f]{4}', cells[0].strip('`')):
            continue
        face = cells[0].strip('`').upper()
        for book in re.findall(r'[BR]', cells[1].upper()) or ['B', 'R']:
            out.setdefault((book, face), cells[3].replace('†', '').strip())
    return out


def speaker_of(mid, jp, fmap, last):
    m = re.search(r'\{face:([0-9A-F]{4})\}', jp)
    if not m:
        return last if last else '?'
    if m[1] == '00FF':
        return 'no portrait (partner/offscreen?)'
    return fmap.get((mid[0], m[1]), 'face %s' % m[1])


def split(nums):
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / 'build').mkdir(exist_ok=True)
    fmap = faces()
    terms = glossary_rows()
    for p in sorted(EV.glob('*.json')):
        if nums and p.stem not in nums:
            continue
        rows, last = [], None
        for e in json.loads(p.read_text(encoding='utf-8')):
            if 'jp' not in e:
                continue
            sp = speaker_of(e['id'], e['jp'], fmap, None)
            if not e.get('en'):
                rows.append('%s\t%s\t%s' % (e['id'], sp, e['jp']))
            last = sp
        if not rows:
            continue
        b = 'e' + p.stem
        (TL / (b + '.tsv')).write_text('\n'.join(rows) + '\n', encoding='utf-8', newline='\n')
        alljp = ''.join(r.split('\t')[2] for r in rows)
        hit = [r for r in terms if any(j and j in alljp for j in re.split(r'\s*/\s*', r[0]))]
        (ROOT / 'build' / ('terms_%s.txt' % b)).write_text(
            '\n'.join(' | '.join(r) for r in hit) + '\n', encoding='utf-8', newline='\n')
        print(b, len(rows), 'entries,', len(hit), 'terms')


def glossary_rows():
    rows = []
    for line in (ROOT / 'glossary.md').read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if line.startswith('|') and len(cells) >= 3 and cells[0] not in ('JP', '---') and not cells[0].startswith('-'):
            rows.append(cells)
    return rows


def read_tsv(path):
    out = {}
    for n, line in enumerate(Path(path).read_text(encoding='utf-8-sig').splitlines(), 1):
        if not line.strip():
            continue
        if '\t' not in line:
            raise ValueError('%s:%d: no TAB' % (path, n))
        k, v = line.split('\t', 1)
        if k in out:
            raise ValueError('%s:%d: duplicate id %s' % (path, n, k))
        out[k] = v
    return out


def check(batch, quiet=False):
    src = TL / (batch + '.tsv')
    jp = {}
    for line in src.read_text(encoding='utf-8').splitlines():
        k, _, j = line.split('\t', 2)
        jp[k] = j
    try:
        en = read_tsv(TL / (batch + '.out.tsv'))
    except (OSError, ValueError) as e:
        print('ERROR', e)
        return 1
    errs = []
    for k in jp:
        if k not in en:
            errs.append('%s: missing' % k)
    for k in en:
        if k not in jp:
            errs.append('%s: not in batch' % k)
    for k, v in en.items():
        if k in jp:
            if '\t' in v or '\\u' in v:
                errs.append('%s: tab or \\u escape' % k)
            for e in lint.lint_event(jp[k], v):
                errs.append('%s: %s' % (k, e))
    for e in errs:
        print(e)
    if not errs and not quiet:
        print('OK', batch, len(en), 'entries')
    return 1 if errs else 0


def merge(batch):
    if check(batch, quiet=True):
        print('merge refused: fix the errors above')
        return 1
    en = read_tsv(TL / (batch + '.out.tsv'))
    n = 0
    for p in sorted(EV.glob('*.json')):
        data = json.loads(p.read_text(encoding='utf-8'))
        hit = 0
        for e in data:
            if e['id'] in en and 'jp' in e:
                e['en'] = en[e['id']]
                hit += 1
        if hit:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
            n += hit
    print('merged', n, 'of', len(en))
    return 0 if n == len(en) else 1


def main():
    cmd = sys.argv[1]
    if cmd == 'split':
        split(sys.argv[2:])
        return 0
    return {'check': check, 'merge': merge}[cmd](sys.argv[2])


if __name__ == '__main__':
    sys.exit(main())
