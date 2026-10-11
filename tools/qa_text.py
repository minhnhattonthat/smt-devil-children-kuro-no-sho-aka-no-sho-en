"""Pick screenshots that show (new) dialogue text and build a contact sheet of the text box area.

  python -X utf8 tools/qa_text.py DIR [--out DIR/text_sheet.png] [--scale 2]
Keeps frames whose box area (y 140-230) has white text pixels and differs from the last kept frame.
"""
import argparse
from pathlib import Path

from PIL import Image


def text_pixels(im):
    px = im.load()
    w, h = im.size
    return frozenset((x, y) for y in range(int(h * 0.58), int(h * 0.96)) for x in range(w)
                     if px[x, y][:3] == (255, 255, 255))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dir')
    ap.add_argument('--out')
    ap.add_argument('--scale', type=int, default=2)
    a = ap.parse_args()
    d = Path(a.dir)
    kept, last = [], frozenset()
    for p in sorted(d.glob('f*.png')):
        im = Image.open(p).convert('RGB')
        t = text_pixels(im)
        if len(t) > 20 and len(t ^ last) > 20:
            kept.append((p.stem, im))
        if len(t) > 20:
            last = t
    # keep the fullest frame of each run of growing text (typing): drop a frame if the next one contains it
    final = [k for i, k in enumerate(kept)
             if not (i + 1 < len(kept) and text_pixels(k[1]) <= text_pixels(kept[i + 1][1]))]
    if not final:
        print('no text frames')
        return 1
    w, h = final[0][1].size
    crop = (0, int(h * 0.55), w, h)
    ch = crop[3] - crop[1]
    cols = 2
    rows = (len(final) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w * a.scale, rows * ch * a.scale), (60, 0, 60))
    for i, (name, im) in enumerate(final):
        tile = im.crop(crop).resize((w * a.scale, ch * a.scale), Image.NEAREST)
        sheet.paste(tile, ((i % cols) * w * a.scale, (i // cols) * ch * a.scale))
    out = a.out or str(d / 'text_sheet.png')
    sheet.save(out)
    print(out, ' '.join(n for n, _ in final))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
