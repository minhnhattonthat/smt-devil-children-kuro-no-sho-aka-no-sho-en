"""Graphics text replacement in 8bpp TIMs inside DEVIL.PAC (book menu, title screens).

Each edit: erase the JP label (pixels in a box that look like the label: low saturation and bright), inpaint
them from the surroundings, draw English with a TrueType font, then map every pixel back to the TIM's own palette.

  python -X utf8 tools/gfx.py preview OUTDIR      render edited TIMs from work/orig/tree/DEVIL.PAC to PNGs
build.py calls apply(pac_bytearray).
"""
import struct
import sys
from collections import Counter
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
# green-keyed "disabled Continue" sprite: the game draws it exactly over menu line 2 ('match' = that edit's index)
STRIP = {'box': (134, 240, 200, 255), 'text': 'Continue', 'kind': 'sprite', 'match': 2}
TITLE_B = [
    {'kind': 'logo', 'box': (2, 72, 196, 141), 'sub_box': (58, 46, 145, 77), 'text': ('DEVIL', 'CHILDREN'),
     'text_box': (14, 74, 188, 140), 'sub': [(54, 57, 'Shin Megami Tensei')]},
    {'box': (28, 150, 101, 173), 'text': 'Black Book', 'size': 13},
    {'box': (16, 186, 84, 205), 'text': 'New Game', 'kind': 'pixel'},
    {'box': (16, 205, 84, 223), 'text': 'Continue', 'kind': 'pixel'},
    STRIP,
]
TITLE_R = [
    {'kind': 'logo', 'box': (14, 74, 196, 141), 'sub_box': (80, 44, 155, 75), 'text': ('DEVIL', 'CHILDREN'),
     'text_box': (92, 74, 196, 140), 'ref': (2, 1), 'sub': [(86, 53, 'Shin Megami Tensei')],
     'fix': {'plaque': (90, 82), 'haze_box': (66, 88, 98, 127), 'yellow_x': 80, 'tail_box': (80, 100, 98, 134), 'wing_box': (90, 118, 150, 142),
             'left_box': (14, 72, 46, 146), 'girl_x': 30}},
    {'box': (148, 150, 223, 168), 'text': 'Red Book', 'size': 13},
    {'box': (172, 188, 242, 207), 'text': 'New Game', 'kind': 'pixel'},
    {'box': (172, 207, 242, 225), 'text': 'Continue', 'kind': 'pixel'},
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


def label_mask(im, box, sat=48, light=90, grow=True):
    px = im.load()
    x0, y0, x1, y1 = box
    m = set()
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if max(r, g, b) - min(r, g, b) < sat and max(r, g, b) >= light:
                m.add((x, y))
    if not grow:
        return m
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


def grow(m, r, box):
    x0, y0, x1, y1 = box
    return {(x + dx, y + dy) for x, y in m for dx in range(-r, r + 1) for dy in range(-r, r + 1)
            if x0 <= x + dx < x1 and y0 <= y + dy < y1}


def components(m, minsize):
    """Points of m in 8-connected groups of at least minsize."""
    left, keep = set(m), set()
    while left:
        grp, todo = set(), [left.pop()]
        while todo:
            x, y = todo.pop()
            grp.add((x, y))
            for q in ((x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                if q in left:
                    left.remove(q)
                    todo.append(q)
        if len(grp) >= minsize:
            keep |= grp
    return keep


def text_mask(text, font, size, at):
    """Pixels of text rendered at (x, y), scaled to size=(w, h)."""
    f = ImageFont.truetype(font, 96)
    l, t, r, b = f.getbbox(text)
    m = Image.new('L', (r - l, b - t))
    ImageDraw.Draw(m).text((-l, -t), text, font=f, fill=255)
    m = m.resize(size, Image.LANCZOS).load()
    return {(at[0] + x, at[1] + y) for y in range(size[1]) for x in range(size[0]) if m[x, y] >= 128}


def fix_art(im, orig, f):
    """Red title: the girl and the monster's tail overlap the old logo. Put the plaque colour back where the logo
    erase left light haze, restore the tail from the original, and wipe logo leftovers on the girl's left."""
    import colorsys
    px, op = im.load(), orig.load()
    hsv = lambda c: colorsys.rgb_to_hsv(*(k / 255 for k in c))
    plaque = px[f['plaque']]
    x0, y0, x1, y1 = f['haze_box']
    for y in range(y0, y1):
        for x in range(x0, x1):
            h, s, v = hsv(px[x, y])
            if (s < 0.15 and v > 0.8) or (x >= f['yellow_x'] and 45 / 360 <= h <= 65 / 360 and s > 0.25 and v > 0.7):
                px[x, y] = plaque
    x0, y0, x1, y1 = f['tail_box']
    for y in range(y0, y1):
        for x in range(x0, x1):
            h, s, v = hsv(op[x, y])
            if (h < 20 / 360 or h > 330 / 360) and s > 0.3 and v > 0.25:
                px[x, y] = op[x, y]
    x0, y0, x1, y1 = f['wing_box']  # the monster's wings stay in front of the lettering
    for y in range(y0, y1):
        for x in range(x0, x1):
            h, s, v = hsv(op[x, y])
            if s < 0.3 and v > 0.75:
                px[x, y] = op[x, y]
    x0, y0, x1, y1 = f['left_box']
    for y in range(y0, y1):
        for x in range(x0, x1):
            h, s, v = hsv(px[x, y])
            if (h < 12 / 360 or h > 330 / 360) and s > 0.2 and not (v < 0.25 and x < 36):
                continue  # the girl
            if (x < f['girl_x'] or (v < 0.4 and (x < 36 or (y >= 110 and s < 0.7) or (y >= 95 and s < 0.5)))
                    or (36 / 360 <= h <= 65 / 360 and s > 0.5 and y >= 95)):
                px[x, y] = px[x0 - 2, y]  # page white


LOGO = {}  # logo pixels -> colour from the Black title (edited first), reused to find the same logo under Red's girl


def edit_logo(im, e):
    """Big katakana logo + red kanji line: erase, refill from the surrounding plaque/background, draw English.
    Characters standing in front of the logo (bright non-logo pixels) stay on top."""
    import colorsys
    import random
    px = im.load()
    orig = im.copy()
    x0, y0, x1, y1 = e['box']
    sx0, sy0, sx1, sy1 = e['sub_box']
    box = (x0, sy0, x1, y1)
    hsv = {q: colorsys.rgb_to_hsv(*(c / 255 for c in px[q])) for q in ((x, y) for y in range(sy0, y1) for x in range(x0, x1))}
    white = {q for q, (h, s, v) in hsv.items() if s < 0.12 and v > 0.85}
    warm = {q for q, (h, s, v) in hsv.items() if 12 / 360 <= h <= 65 / 360 and s > 0.3 and v > 0.3 and q[1] >= y0}
    fill = {q for q in warm if hsv[q][1] > 0.8 and hsv[q][2] > 0.55}
    red = {q for q, (h, s, v) in hsv.items() if s > 0.5 and v > 0.3 and (h < 12 / 360 or h > 340 / 360)
           and sx0 <= q[0] < sx1 and sy0 <= q[1] < sy1}
    if 'ref' not in e:
        dark = {q for q in grow(fill, 8, box) if hsv[q][2] < 0.6 and hsv[q][1] < 0.5}
        logo = ((warm & grow(fill, 3, box)) | dark) - white
        for q in [q for q in hsv if q[0] < e['text_box'][0] + 5 and e['text_box'][1] <= q[1] < e['text_box'][3]]:
            px[q] = px[(x0, q[1])]  # left margin of the logo: plain background
        LOGO.update({q: px[q] for q in logo})
    else:  # same katakana artwork shifted (the kanji line is not): logo where Black's logo colour is still there
        dx, dy = e['ref']
        logo = {(x + dx, y + dy) for (x, y), c in LOGO.items()
                if (x + dx, y + dy) in hsv and sum((a - b) ** 2 for a, b in zip(px[x + dx, y + dy], c)) < 60 ** 2}
    tx0, ty0, tx1, ty1 = e['text_box']
    logo |= grow(red, 2, box) - white
    logo |= {q for q in grow(red, 5, box) if (hsv[q][0] < 15 / 360 or hsv[q][0] > 330 / 360) and hsv[q][1] > 0.12 and hsv[q][2] < 0.8}  # pink haze
    logo |= {(x, y) for x, y in warm if tx0 <= x < tx1 and ty0 <= y < ty1}  # nothing in front of the logo there
    bright = {q for q, (h, s, v) in hsv.items() if v > 0.5} - white - logo
    protect = grow(components(bright, 30), 1, box) - {q for q in logo if q in warm or q in red}
    if 'ref' in e:  # strict match misses edge pixels whose colour differs between the two titles
        logo = grow(logo, 3, box) - white
        logo |= {q for q in grow(logo, 4, box) if hsv[q][1] < 0.15 and hsv[q][2] > 0.55}  # grey edge over the white
    logo -= protect
    # logo gradient by row, from the original fill
    ys = sorted({y for _, y in fill})
    rows = {y: [px[q] for q in fill if q[1] == y] for y in ys}
    grad = [tuple(sum(c[k] for c in rows[y]) // len(rows[y]) for k in range(3)) for y in ys]
    ink = Counter(px[q] for q in red).most_common(1)[0][0]
    # refill layer by layer from the edge: each pixel copies a random known neighbour (keeps marble speckle / white)
    rnd = random.Random(1)
    todo = set(logo)
    while todo:
        layer = {}
        for x, y in sorted(todo):
            nb = [q for q in ((x + a, y + b) for a in (-1, 0, 1) for b in (-1, 0, 1))
                  if q not in todo and q not in protect and 0 <= q[0] < im.width and 0 <= q[1] < im.height]
            if nb:
                layer[(x, y)] = px[rnd.choice(nb)]
        if not layer:
            break
        for q, c in layer.items():
            px[q] = c
        todo -= set(layer)
    # English logo: each line stretched to the text box width
    lines = e['text']
    gap = e.get('gap', 2)
    lh = (ty1 - ty0 - 8 - gap * (len(lines) - 1)) // len(lines)
    draw = {}
    full = (0, 0, im.width, im.height)
    for i, s in enumerate(lines):
        ly = ty0 + 4 + i * (lh + gap)
        m = text_mask(s, str(FONTS / 'impact.ttf'), (tx1 - tx0 - 8, lh), (tx0 + 4, ly))
        for q in grow(m, 4, full):
            draw.setdefault(q, (72, 72, 88))
        for q in grow(m, 2, full):
            draw[q] = (8, 8, 16)
        for q in m:
            draw[q] = grad[min(len(grad) - 1, (q[1] - ly) * len(grad) // lh)]
    for q, c in draw.items():
        if q not in protect or q[0] < tx0 + 10:  # left edge: logo wins over stray character pixels
            px[q] = c
    for x, y, s in e['sub']:
        draw_pixel_text(im, x, y, s, ink, (24, 8, 16))
    if 'fix' in e:
        fix_art(im, orig, e['fix'])


def edit_tim(t, edits):
    from collections import Counter
    im = tim.to_image(t).convert('RGB')
    px = im.load()
    done = {}  # edit index -> (JP light-pixel mask, English text position)
    for i, e in enumerate(edits):
        x0, y0, x1, y1 = e['box']
        kind = e.get('kind', 'label')
        if kind == 'logo':
            edit_logo(im, e)
            continue
        if kind == 'sprite':  # key-colour background: clear to the key, draw crisp text in the sprite's colour
            cols = Counter(px[x, y] for y in range(y0, y1) for x in range(x0, x1))
            key = cols.most_common(1)[0][0]
            tones = sorted((c for c, n in cols.most_common(4) if c != key and n > 20), key=sum)
            ink, edge = tones[-1], tones[0]  # opaque 2-tone sprite: grey fill (112) + darker outline (64)
            pts = {(x, y) for y in range(y0, y1) for x in range(x0, x1) if px[x, y] != key}
            for q in pts:
                px[q] = key
            mmask, (ex, ey) = done[e['match']]
            ox, oy = best_offset(pts, mmask)  # sprite pixel + (ox, oy) = menu pixel on screen
            draw_pixel_text(im, ex - ox, ey - oy, e['text'], ink, edge)
            continue
        mask = label_mask(im, e['box'])
        colour = max((px[q] for q in mask), key=sum) if mask else (220, 220, 220)
        top = min((y for _, y in mask), default=y0)
        left = min((x for x, _ in mask), default=x0)
        core = label_mask(im, e['box'], grow=False)
        inpaint(im, mask)
        if kind == 'pixel':
            draw_pixel_text(im, left + 1, top + 1, e['text'], colour, (0, 0, 16))
            done[i] = (core, (left + 1, top + 1))
        else:
            draw_label(im, e['box'], e['text'], e['size'], colour)
    return im


def best_offset(a, b):
    """(dx, dy) maximising overlap of point set a shifted onto point set b (bbox-aligned start, +-6 search)."""
    ax, ay = min(x for x, _ in a), min(y for _, y in a)
    bx, by = min(x for x, _ in b), min(y for _, y in b)
    best = (-1, (bx - ax, by - ay))
    for dx in range(bx - ax - 6, bx - ax + 7):
        for dy in range(by - ay - 6, by - ay + 7):
            score = sum((x + dx, y + dy) in b for x, y in a)
            best = max(best, (score, (dx, dy)))
    return best[1]


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


# ---- 4bpp menu sheet (DEVIL.PAC 0x26D3800, 256x240): palette index 0 = key, 1 white, 2/3 greys, 4-15 button
# bodies (other CLUT rows shade them). Buttons are 47x16 cells, labels are white text on the key colour.
MENU_SHEET = 0x026D3800
BUTTONS = {  # (x0, y0, x1, y1): English
    (1, 32, 47, 47): 'Vinecom', (49, 32, 95, 47): 'Items', (97, 32, 143, 47): 'Save',
    (1, 48, 47, 63): 'Magic', (49, 48, 95, 63): 'Settings', (97, 48, 143, 63): 'DeviPhone',
    (1, 64, 47, 79): 'Status', (49, 64, 95, 79): 'Dismiss', (97, 64, 143, 79): 'Devidas',
    (1, 80, 47, 95): 'Arrange', (49, 80, 95, 95): 'Options', (97, 80, 143, 95): 'Set',
    (1, 96, 47, 111): 'Summon', (49, 96, 95, 111): 'Send', (97, 96, 143, 111): 'View',
    (1, 112, 47, 127): 'Disc', (49, 112, 95, 127): 'Load', (97, 112, 143, 127): 'Map',
    (1, 128, 71, 143): 'Vine Center', (73, 128, 143, 143): 'Friends',
    (1, 144, 47, 159): 'Stamina', (49, 144, 95, 159): 'Fighting', (97, 144, 143, 159): 'Mental',
    (1, 160, 47, 175): 'Deposit', (49, 160, 95, 175): 'Withdraw', (97, 160, 143, 175): 'Start',
    (1, 176, 47, 191): 'Fast', (49, 176, 95, 191): 'Normal', (97, 176, 143, 191): 'Thorough',
    (1, 192, 47, 207): 'OK', (49, 192, 95, 207): 'Cancel', (97, 192, 143, 207): 'Reset',
    (217, 32, 255, 47): 'ABC', (217, 48, 255, 63): 'abc', (217, 64, 255, 79): 'Delete', (217, 80, 255, 95): 'Done',
}
LABELS = {  # (x0, y0, x1, y1): English, drawn with the game's 8x8 font
    (144, 34, 180, 47): 'Race', (144, 49, 180, 62): 'Name', (144, 65, 180, 78): 'Level',
    (144, 81, 180, 94): 'Elem.', (144, 97, 180, 110): 'Combo', (144, 113, 180, 126): 'Number',
    (180, 32, 217, 40): 'Common', (180, 40, 217, 48): 'Elite', (180, 48, 217, 56): 'General', (180, 56, 217, 64): 'King',
    (180, 72, 217, 80): 'God', (180, 80, 217, 88): 'Akuma', (180, 88, 217, 96): 'Divine', (180, 96, 217, 104): 'Oni',
    (180, 104, 217, 112): 'Specter', (180, 112, 217, 120): 'Draco', (180, 120, 217, 128): 'Yoma',
    (180, 128, 217, 136): 'Mutant', (180, 136, 217, 144): 'Boss', (180, 144, 217, 152): 'Beast',
    (180, 152, 217, 160): 'Combo', (180, 160, 226, 168): 'MP Cost', (180, 168, 226, 176): 'HP Cost',
    (144, 136, 177, 144): '????', (144, 144, 177, 152): 'Level', (144, 152, 177, 160): 'Number',
    (144, 160, 177, 168): 'Name', (144, 168, 177, 176): 'Class', (144, 176, 177, 184): 'Race',
    (144, 184, 177, 192): 'Element', (144, 192, 177, 200): 'Select', (144, 200, 217, 208): 'Search mode',
    (0, 224, 140, 232): 'X Button / SELECT Button /',
}


class Sheet4:
    """Index-level access to a 4bpp TIM inside a bytearray."""
    def __init__(self, pac, off):
        self.t = tim.parse(bytes(pac[off:off + 0x10000]), 0)
        self.pac, self.base = pac, off + self.t['end'] - len(self.t['data'])
        self.row = self.t['w'] * 2

    def get(self, x, y):
        b = self.pac[self.base + y * self.row + x // 2]
        return (b >> 4) if x & 1 else b & 15

    def set(self, x, y, v):
        o = self.base + y * self.row + x // 2
        b = self.pac[o]
        self.pac[o] = (b & 0x0F) | (v << 4) if x & 1 else (b & 0xF0) | v


def font8(pac):
    """{ascii: (rows of 8 values 0-3, width)} from the game's 8x8 font (TXS image, glyph per tools/../build map8)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import build
    m = build.map8()
    out = {}
    for c in range(0x21, 0x7F):
        g = m[c]
        if not g:
            continue
        rows = []
        for yy in range(8):
            row = []
            for xx in range(8):
                lin = ((g >> 5) * 8 + 4 + yy) * 1024 + (g & 31) * 8 - 32 + xx
                b = pac[0x15D8010 + lin // 2]
                v = (b >> 4) if lin & 1 else b & 15
                row.append(v)
            rows.append(row)
        cols = [x for x in range(8) if any(r[x] for r in rows)]
        lo = cols[0] if cols else 0
        hi = cols[-1] if cols else 2
        rows = [r[lo:hi + 1] for r in rows]
        out[chr(c)] = (rows, hi - lo + 1)
    return out


def draw_menu_sheet(pac):
    import font
    s = Sheet4(pac, MENU_SHEET)
    glyphs = font.load_en(Path(__file__).resolve().parent.parent / 'font' / 'en16.txt')
    for (x0, y0, x1, y1), text in BUTTONS.items():
        for y in range(y0, y1):  # erase: text pixels take the row's most common body index
            body = Counter(s.get(x, y) for x in range(x0, x1) if s.get(x, y) >= 4)
            fill = body.most_common(1)[0][0] if body else 5
            for x in range(x0, x1):
                if s.get(x, y) in (1, 2, 3):
                    s.set(x, y, fill)
        w = sum(glyphs[font.EN_BASE + ord(c)][1] for c in text) - 1
        xe = x1 - 5 if x1 == 143 else x1  # the search tabs sample the last columns of the right-hand buttons
        gap = 1 if w <= xe - x0 - 2 else 0  # tight spacing when the word would not fit the button
        w -= (1 - gap) * (len(text) - 1)
        x = x0 + max(1, (xe - x0 - w) // 2)
        for c in text:
            px, adv = glyphs[font.EN_BASE + ord(c)]
            for yy in range(4, 15):
                for xx in range(16):
                    if px[yy][xx] == 1 and x + xx < xe - 1 and y0 + yy - 1 < y1:
                        s.set(x + xx, y0 + yy - 1, 1)
            x += adv - (1 - gap)
    f5 = font5()
    for (x0, y0, x1, y1), text in LABELS.items():
        for y in range(y0, y1):
            for x in range(x0, x1):
                if s.get(x, y) in (1, 2, 3):
                    s.set(x, y, 0)
        x = x0 + (0 if x0 == 0 else 3)  # the game's cells start ~3 px inside the box: text at x0 lost its first letter
        top = y0 + max(0, (y1 - y0 - 6) // 2)
        if x0 == 144 and y0 < 120:  # Devidas search tabs: centred
            w = sum(2 if c == ' ' else len(f5[c][0]) + 1 for c in text.upper()) - 1
            x = x0 + 3 + max(0, (x1 - x0 - 3 - w) // 2)
        for c in text.upper():
            if c == ' ':
                x += 2
                continue
            rows = f5[c]
            for yy, r in enumerate(rows):
                for xx, ch in enumerate(r):
                    if ch == '#' and x + xx + 1 < x1:
                        s.set(x + xx, top + yy, 1)
                        if s.get(x + xx + 1, top + yy + 1) == 0:
                            s.set(x + xx + 1, top + yy + 1, 3)
            x += len(rows[0]) + 1


def font5():
    """font/en5.txt: {char: [row strings]}, 5 rows, '#' = pixel."""
    out = {}
    for line in (Path(__file__).resolve().parent.parent / 'font' / 'en5.txt').read_text(encoding='utf-8').splitlines():
        if line and not line.startswith('#'):
            c, *rows = line.split(' ')
            out[c] = rows
    return out


class Raw4:
    """Index access to the font TXS image in DEVIL.PAC (1024 px wide, 4bpp)."""
    def __init__(self, pac, base=0x15D8010, row=512):
        self.pac, self.base, self.row = pac, base, row

    get = Sheet4.get
    set = Sheet4.set


# battle command buttons in the TXS image: 4 x 3 cells, body values 5-9 (row gradient), text values 1-4 (1 = ink)
BATTLE_BUTTONS = {}
for _r, _row in enumerate((('Fight', 'Auto', 'Talk', 'Combo'), ('Escape', 'Status', 'Attack', 'Magic'),
                           ('Special', 'Items', 'Call', 'Repeat'))):
    for _c, _t in enumerate(_row):
        BATTLE_BUTTONS[(226 + 32 * _c, 4 + 16 * _r, 254 + 32 * _c, 19 + 16 * _r)] = _t


def draw_battle_buttons(pac):
    import font
    s = Raw4(pac)
    glyphs = font.load_en(Path(__file__).resolve().parent.parent / 'font' / 'en16.txt')
    for (x0, y0, x1, y1), text in BATTLE_BUTTONS.items():
        for y in range(y0, y1):
            body = Counter(s.get(x, y) for x in range(x0, x1) if s.get(x, y) >= 5)
            fill = body.most_common(1)[0][0] if body else 5
            for x in range(x0, x1):
                if 1 <= s.get(x, y) <= 4:
                    s.set(x, y, fill)
        w = sum(glyphs[font.EN_BASE + ord(c)][1] for c in text) - 1
        gap = 1 if w <= x1 - x0 else 0
        w -= (1 - gap) * (len(text) - 1)
        x = x0 + max(0, (x1 - x0 - w) // 2)
        for c in text:
            px, adv = glyphs[font.EN_BASE + ord(c)]
            for yy in range(4, 15):
                for xx in range(16):
                    if px[yy][xx] == 1 and x + xx < x1 and y0 + yy - 1 < y1:
                        s.set(x + xx, y0 + yy - 1, 1)
            x += adv - (1 - gap)


# status / battle-UI text labels in the same TXS image (no button body: text on the key index 0).
# (box, English, body index, shadow index). Gradient labels use 13/11 (light), the command list uses 8/1 (grey).
STATUS_LABELS = [
    ((223, 115, 272, 130), 'Next Lv', 13, 11, 2), ((273, 115, 311, 130), 'Class', 13, 11, -1),
    ((312, 115, 352, 130), 'Element', 13, 11), ((353, 115, 393, 130), 'Race', 13, 11, -1),
    ((335, 133, 393, 147), 'HP Cost', 13, 11), ((335, 149, 393, 163), 'MP Cost', 13, 11),
    ((351, 162, 403, 178), 'Surrender', 8, 1), ((351, 178, 403, 194), 'Combo', 8, 1),
    ((351, 193, 403, 209), 'Go for it!', 8, 1), ((351, 211, 403, 227), 'Call', 8, 1),
]


def draw_status_labels(pac):
    import font
    s = Raw4(pac)
    glyphs = font.load_en(Path(__file__).resolve().parent.parent / 'font' / 'en16.txt')
    for (x0, y0, x1, y1), text, body, shade, *ox in STATUS_LABELS:
        for y in range(y0, y1):
            for x in range(x0, x1):
                s.set(x, y, 0)
        w = sum(glyphs[font.EN_BASE + ord(c)][1] for c in text) - 1
        gap = 1 if w <= x1 - x0 else 0
        w -= (1 - gap) * (len(text) - 1)
        x = x0 + (2 if body == 8 else 0) + (ox[0] if ox else 0)  # left-aligned like the Japanese labels
        top = y0 + max(0, (y1 - y0 - 11) // 2) - 3  # glyph row 4 (cap top) lands at y0 + (h - 9) / 2
        for c in text:
            px, adv = glyphs[font.EN_BASE + ord(c)]
            for yy in range(4, 15):
                for xx in range(16):
                    v = px[yy][xx]
                    if v and x + xx < x1 and y0 <= top + yy < y1:
                        s.set(x + xx, top + yy, body if v == 1 else shade)
            x += adv - (1 - gap)


def apply(pac):
    for off, edits in EDITS.items():
        t = tim.parse(bytes(pac[off:off + 0x20000]), 0)
        im = edit_tim(t, edits)
        quantize_into(t, im, pac, off)
    draw_menu_sheet(pac)
    draw_battle_buttons(pac)
    draw_status_labels(pac)


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
