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
    {'box': (28, 150, 101, 173), 'text': 'Black Book', 'size': 13},
    {'box': (16, 186, 84, 205), 'text': 'New Game', 'kind': 'pixel'},
    {'box': (16, 205, 84, 223), 'text': 'Continue', 'kind': 'pixel'},
    STRIP,
]
TITLE_R = [
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


def edit_tim(t, edits):
    from collections import Counter
    im = tim.to_image(t).convert('RGB')
    px = im.load()
    done = {}  # edit index -> (JP light-pixel mask, English text position)
    for i, e in enumerate(edits):
        x0, y0, x1, y1 = e['box']
        kind = e.get('kind', 'label')
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
    (144, 81, 180, 94): 'Element', (144, 97, 180, 110): 'Combo', (144, 113, 180, 126): 'Number',
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
        gap = 1 if w <= x1 - x0 - 2 else 0  # tight spacing when the word would not fit the button
        w -= (1 - gap) * (len(text) - 1)
        x = x0 + max(1, (x1 - x0 - w) // 2)
        for c in text:
            px, adv = glyphs[font.EN_BASE + ord(c)]
            for yy in range(4, 15):
                for xx in range(16):
                    if px[yy][xx] == 1 and x + xx < x1 - 1 and y0 + yy - 1 < y1:
                        s.set(x + xx, y0 + yy - 1, 1)
            x += adv - (1 - gap)
    f5 = font5()
    for (x0, y0, x1, y1), text in LABELS.items():
        for y in range(y0, y1):
            for x in range(x0, x1):
                if s.get(x, y) in (1, 2, 3):
                    s.set(x, y, 0)
        x = x0
        top = y0 + max(0, (y1 - y0 - 6) // 2)
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
    ((223, 115, 272, 130), 'Next Lv', 13, 11, 2), ((273, 115, 311, 130), 'Class', 13, 11),
    ((312, 115, 352, 130), 'Element', 13, 11), ((353, 115, 393, 130), 'Race', 13, 11, 4),
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
