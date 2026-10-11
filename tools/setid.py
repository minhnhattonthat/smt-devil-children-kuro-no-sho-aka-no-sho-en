"""Set English for ids: python setid.py FILE.tsv  (id<TAB>English) - updates script/*/ JSON."""
import glob, json, sys
fix = {}
for line in open(sys.argv[1], encoding='utf-8').read().splitlines():
    if line.strip():
        k, v = line.split('\t', 1)
        fix[k] = v
n = 0
for f in sorted(glob.glob('script/*/*.json')):
    data = json.load(open(f, encoding='utf-8'))
    hit = False
    for e in data:
        if e['id'] in fix and 'jp' in e:
            e['en'] = fix[e['id']]
            hit = True
            n += 1
    if hit:
        open(f, 'w', encoding='utf-8', newline='\n').write(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
print('set', n, 'of', len(fix))
