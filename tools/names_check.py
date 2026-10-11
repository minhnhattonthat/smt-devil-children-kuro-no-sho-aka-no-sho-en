"""Name consistency: if a JP name from docs/names.md (demons, speaker labels) or a glossary row occurs in a line,
its English form must occur in the translation (longest JP match wins; case-insensitive).

  python -X utf8 tools/names_check.py [--sub event] [--limit 50]
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = re.compile(r'\{[^}]*\}|\[[0-9A-F]{4}\]')
OK = {('B:417A8', 'ニタニタ')}  # the word itself (a grin), not the Devil's name


def name_pairs():
    """[(jp, [accepted en forms])], longest JP first. names.md demon + label tables, glossary first column."""
    pairs = {}
    for line in (ROOT / 'docs' / 'names.md').read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 3 and re.fullmatch(r'[0-9A-F]{2,3}', cells[0]):
            jp, en = cells[1], cells[2]
            if len(jp) >= 3 and en and 'not a label' not in line and re.search('[ァ-ヶ]', jp):
                pairs.setdefault(jp, set()).add(en)
    for line in (ROOT / 'glossary.md').read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if line.startswith('|') and len(cells) >= 3 and cells[0] not in ('JP', '---') and not cells[0].startswith('-'):
            jps = re.split(r'\s*/\s*', cells[0])
            ens = re.split(r'\s*/\s*', re.sub(r'\s*\([^)]*\)', '', cells[1]))
            if len(jps) == len(ens):
                for j, e in zip(jps, ens):
                    if len(j) >= 3 and re.fullmatch(r'[ァ-ヶー・]+', j):
                        pairs.setdefault(j, set()).add(e)
    return sorted(pairs.items(), key=lambda kv: -len(kv[0]))


def check(jp, en, pairs):
    text = TOKEN.sub('', jp)
    low = TOKEN.sub('', en).lower()
    missing = []
    for j, ens in pairs:
        if j in text:
            text = text.replace(j, '\0')
            if not any(e.lower() in low for e in ens):
                missing.append('%s -> %s' % (j, '/'.join(sorted(ens))))
    return missing


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sub', default='event')
    ap.add_argument('--limit', type=int, default=50)
    a = ap.parse_args()
    pairs = name_pairs()
    n = 0
    for p in sorted((ROOT / 'script' / a.sub).glob('*.json')):
        for e in json.loads(p.read_text(encoding='utf-8')):
            if e.get('en') and e['en'] != e.get('jp'):
                for m in check(e['jp'], e['en'], pairs):
                    if (e['id'], m.split(' ')[0]) in OK:
                        continue
                    if n < a.limit:
                        print('%s %s: %s | %s' % (p.name, e['id'], m, TOKEN.sub('', e['en'])[:90]))
                    n += 1
    print('names: %d issues' % n)
    return 1 if n else 0


if __name__ == '__main__':
    raise SystemExit(main())
