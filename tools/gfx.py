"""Graphics text replacement in 8bpp TIMs inside DEVIL.PAC (book menu, title screens).

Each edit: erase the JP label (pixels in a box that look like the label: low saturation and bright), inpaint
them from the surroundings, draw English with a TrueType font, then map every pixel back to the TIM's own palette.

  python -X utf8 tools/gfx.py preview OUTDIR      render edited TIMs from work/orig/tree/DEVIL.PAC to PNGs
build.py calls apply(pac_bytearray).
"""
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import tim  # noqa: E402

FONTS = Path('C:/Windows/Fonts')
SERIF = str(FONTS / 'georgiab.ttf')

MENU = [  # book-select menu: three TIMs, one per highlighted entry; label colour taken from the original
    {'box': (20, 88, 105, 117), 'text': 'Black Book', 'size': 15},
    {'box': (152, 88, 236, 117), 'text': 'Red Book', 'size': 15},
    {'box': (96, 188, 170, 207), 'text': 'Webnet', 'size': 12},
]
STRIP = {'box': (134, 240, 200, 255), 'text': 'Continue', 'kind': 'sprite'}  # green-keyed highlight sprite
TITLE_B = [
    {'box': (28, 150, 101, 173), 'text': 'Black Book', 'size': 13},
    {'box': (12, 185, 88, 203), 'text': 'New Game', 'kind': 'pixel'},
    {'box': (12, 203, 88, 223), 'text': 'Continue', 'kind': 'pixel'},
    STRIP,
]
TITLE_R = [
    {'box': (148, 150, 223, 168), 'text': 'Red Book', 'size': 13},
    {'box': (170, 185, 246, 203), 'text': 'New Game', 'kind': 'pixel'},
    {'box': (170, 203, 246, 223), 'text': 'Continue', 'kind': 'pixel'},
    STRIP,
]
EDITS = {
    0x01586800: MENU, 0x01596A20: MENU, 0x015A6C40: MENU,
    0x015B7000: TITLE_B, 0x015C7800: TITLE_R,
}


def draw_pixel_text(im, x, y, text, body, shadow=None):
    """Draw with the game's English 16x16 glyphs (font/en16.txt): body colour, optional drop shadow."""
    import font
    glyphs = font.load_en(Path(__file__).resolve().parent.parent / 'font' / 'en16.txt')
    px = im.load()
    for c in text:
        g, adv = glyphs[font.EN_BASE + ord(c)]
        for yy in range(16):
            for xx in range(16):
                v = g[yy][xx]
                col = body if v == 1 else shadow if v == 3 and shadow else None
                if col and 0 <= x + xx < im.width and 0 <= y + yy - font.EN_TOP < im.height:
                    px[x + xx, y + yy - font.EN_TOP] = col
        x += adv


def label_mask(im, box, sat=48, light=90):
    px = im.load()
    x0, y0, x1, y1 = box
    m = set()
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if max(r, g, b) - min(r, g, b) < sat and max(r, g, b) >= light:
                m.add((x, y))
    # grow by one pixel to take the antialiased edge
    grown = set(m)
    for x, y in m:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if x0 <= x + dx < x1 and y0 <= y + dy < y1:
                    grown.add((x + dx, y + dy))
    return grown


def inpaint(im, mask, rounds=40):
    px = im.load()
    known = {}
    todo = set(mask)
    for _ in range(rounds):
        if not todo:
            break
        new = {}
        for x, y in todo:
            acc = [0, 0, 0]
            n = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                q = (x + dx, y + dy)
                if q not in todo and 0 <= q[0] < im.width and 0 <= q[1] < im.height:
                    c = known.get(q) or px[q]
                    acc = [acc[i] + c[i] for i in range(3)]
                    n += 1
            if n:
                new[(x, y)] = tuple(a // n for a in acc)
        for q, c in new.items():
            known[q] = c
            px[q] = c
        todo -= set(new)


def draw_label(im, box, text, size, colour):
    x0, y0, x1, y1 = box
    font = ImageFont.truetype(SERIF, size)
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = d.textbbox((0, 0), text, font=font)[2:]
    x = x0 + (x1 - x0 - w) // 2
    y = y0 + (y1 - y0 - h) // 2 - 1
    shadow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 230))
    shadow = shadow.filter(ImageFilter.GaussianBlur(0.6))
    im.paste(shadow, (0, 0), shadow)
    d.text((x, y), text, font=font, fill=colour + (255,))
    im.paste(layer, (0, 0), layer)


def edit_tim(t, edits):
    from collections import Counter
    im = tim.to_image(t).convert('RGB')
    px = im.load()
    for e in edits:
        x0, y0, x1, y1 = e['box']
        kind = e.get('kind', 'label')
        if kind == 'sprite':  # key-colour background: clear to the key, draw crisp text in the sprite's colour
            cols = Counter(px[x, y] for y in range(y0, y1) for x in range(x0, x1))
            key = cols.most_common(1)[0][0]
            ink = next((c for c, _ in cols.most_common() if c != key), (128, 64, 160))
            pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if px[x, y] != key]
            top = min(y for _, y in pts) if pts else y0
            left = min(x for x, _ in pts) if pts else x0
            for q in pts:
                px[q] = key
            draw_pixel_text(im, left, top, e['text'], ink)
            continue
        mask = label_mask(im, e['box'])
        colour = max((px[q] for q in mask), key=sum) if mask else (220, 220, 220)
        top = min((y for _, y in mask), default=y0)
        left = min((x for x, _ in mask), default=x0)
        inpaint(im, mask)
        if kind == 'pixel':
            draw_pixel_text(im, left + 1, top + 1, e['text'], colour, (0, 0, 16))
        else:
            draw_label(im, e['box'], e['text'], e['size'], colour)
    return im


def quantize_into(t, im, d, base):
    """Write im back into the 8bpp TIM pixel data (nearest palette colour). d = the whole file (bytearray)."""
    assert t['bpp'] == 8
    cd = t['clut'][4]
    pal = [tim.rgb(struct.unpack_from('<H', cd, i * 2)[0]) for i in range(t['clut'][2])]
    cache = {}
    px = im.load()
    data_off = t['end'] - len(t['data'])
    for y in range(t['h']):
        for x in range(t['pw']):
            c = px[x, y]
            if c not in cache:
                cache[c] = min(range(len(pal)), key=lambda i: sum((pal[i][k] - c[k]) ** 2 for k in range(3)))
            d[base + data_off + y * t['w'] * 2 + x] = cache[c]


def apply(pac):
    for off, edits in EDITS.items():
        t = tim.parse(bytes(pac[off:off + 0x20000]), 0)
        im = edit_tim(t, edits)
        quantize_into(t, im, pac, off)


def main():
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    pac = bytearray((Path(__file__).resolve().parent.parent / 'work' / 'orig' / 'tree' / 'DEVIL.PAC').read_bytes())
    apply(pac)
    for off in EDITS:
        t = tim.parse(bytes(pac[off:off + 0x20000]), 0)
        tim.to_image(t).save(out / ('%08X.png' % off))
    print('wrote', len(EDITS))


if __name__ == '__main__':
    main()
