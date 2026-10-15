"""Overflow check for the demon info screens (work/qa/tour/demon_NNN/s00.png, s01.png) after `tour.py run demons`.
White text must stay inside its box: name box (x 17-126), skill list (x 137-246), description bar (x 9-246).
  python -X utf8 tools/debug/check_demons.py
Prints the demons whose text touches a box border and writes work/qa/tour/demons_flagged.png (crops)."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'work/qa/tour'
# (shot, name, x0, x1, y0, y1): text white pixels in [x0, x1] x [y0, y1]; flagged when one reaches x1
CHECKS = [('s00', 'name', 19, 123, 199, 221), ('s00', 'header name next to EXP', 40, 146, 30, 42), ('s01', 'skills', 139, 243, 78, 172), ('s01', 'description', 11, 243, 199, 221),
          ('s01', 'cost', 139, 243, 174, 196)]


def main():
    flagged = []
    for d in sorted(OUT.glob('demon_*')):
        for shot, what, x0, x1, y0, y1 in CHECKS:
            p = d / f'{shot}.png'
            if not p.exists():
                continue
            im = Image.open(p).convert('RGB')
            px = im.load()
            hit = [x for y in range(y0, y1 + 1) for x in range(x1 - 1, x1 + 3) if px[x, y] == (255, 255, 255)]
            if hit:
                flagged.append((d.name, shot, what))
    print(len(flagged), 'flagged')
    for f in flagged:
        print(*f)
    if flagged:
        tiles = [Image.open(OUT / n / f'{s}.png').convert('RGB') for n, s, _ in flagged[:24]]
        sheet = Image.new('RGB', (4 * 256, ((len(tiles) + 3) // 4) * 240))
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % 4) * 256, (i // 4) * 240))
        sheet.save(OUT / 'demons_flagged.png')


if __name__ == '__main__':
    main()
