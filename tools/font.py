"""Main 16x16 font in DEVIL.PAC (TXS block loaded to VRAM 768,256; 1024x256 px at 4bpp).

Glyph g: tpage x = 896 + 64*(g>>9) halfwords (image px 512 + 256*(g>>9)), cell col g&15, row (g>>4)&15,
layer = (g>>8)&1 picks CLUT 0x1F0/0x1F1: two 2bpp glyph sets packed into one 4bpp page.

  python -X utf8 tools/font.py sheet PAC OUT.png [--first 0 --count 1024]   labelled glyph sheet
"""
import argparse

from PIL import Image, ImageDraw

TXS_OFF = 0x15D8000          # 'TXS\0' header in DEVIL.PAC
IMG_OFF = TXS_OFF + 0x10
IMG_W = 1024                 # px, 4bpp -> 512 bytes per row
FONT_X = 480                 # image px of tpage 0x1E (found visually: 'A' = 0x23)


def layer_shift(g):
    return 0 if g & 0x100 else 2  # layer 0 = bits 2-3, layer 1 = bits 0-1 (checked on the sheet)


def glyph(pac, g):
    """16x16 list of 2-bit values."""
    x0 = FONT_X + 256 * (g >> 9) + 16 * (g & 15)
    y0 = 16 * ((g >> 4) & 15)
    sh = layer_shift(g)
    rows = []
    for y in range(16):
        row = []
        for x in range(16):
            px = x0 + x
            b = pac[IMG_OFF + (y0 + y) * (IMG_W // 2) + px // 2]
            v = (b >> 4) if px & 1 else (b & 15)
            row.append((v >> sh) & 3)
        rows.append(row)
    return rows


EN_BASE = 0x100   # English glyph code = EN_BASE + ASCII
EN_TOP = 4        # art row 0 lands on cell row 4


def load_en(path):
    """font/en16.txt -> {code: (16x16 values, advance)}. Body '#' = 1, shadow 3 added at (+1,+1)."""
    glyphs, cur = {}, None
    for line in open(path, encoding='utf-8').read().splitlines() + ['']:
        if line.startswith('#') and cur is None or line.startswith('# '):
            continue
        if line.startswith('char '):
            cur = {'code': EN_BASE + int(line.split()[1], 16), 'rows': [], 'width': None}
        elif cur is not None and line.startswith('width '):
            cur['width'] = int(line.split()[1])
        elif cur is not None and line:
            cur['rows'].append(line)
        elif cur is not None:
            px = [[0] * 16 for _ in range(16)]
            body_w = 0
            for y, r in enumerate(cur['rows']):
                for x, c in enumerate(r):
                    if c == '#':
                        px[EN_TOP + y][x] = 1
                        body_w = max(body_w, x + 1)
            for y in range(15, -1, -1):
                for x in range(15, -1, -1):
                    if px[y][x] == 1 and y < 15 and x < 15 and px[y + 1][x + 1] == 0:
                        px[y + 1][x + 1] = 3
            assert body_w <= 14 and len(cur['rows']) + EN_TOP <= 15, hex(cur['code'])
            glyphs[cur['code']] = (px, cur['width'] if cur['width'] is not None else body_w + 1)
            cur = None
    return glyphs


def put_glyph(pac, g, px):
    """Write 16x16 2-bit values into glyph g's layer of the font image (bytearray)."""
    x0 = FONT_X + 256 * (g >> 9) + 16 * (g & 15)
    y0 = 16 * ((g >> 4) & 15)
    sh = layer_shift(g)
    for y in range(16):
        for x in range(16):
            px_ = x0 + x
            o = IMG_OFF + (y0 + y) * (IMG_W // 2) + px_ // 2
            nib_sh = 4 if px_ & 1 else 0
            nib = (pac[o] >> nib_sh) & 15
            nib = (nib & ~(3 << sh)) | (px[y][x] << sh)
            pac[o] = (pac[o] & ~(15 << nib_sh) & 0xFF) | (nib << nib_sh)


def preview(glyphs, text, out, scale=3):
    """Render text with the English glyphs and advances, as the game would (black box)."""
    w = sum(glyphs[EN_BASE + ord(c)][1] for c in text) + 16
    im = Image.new('RGB', (w * scale, 20 * scale), (0, 32, 90))
    dr = ImageDraw.Draw(im)
    pal = {1: (255, 255, 255), 2: (172, 172, 172), 3: (8, 8, 8)}
    x = 4
    for c in text:
        px, adv = glyphs[EN_BASE + ord(c)]
        for yy in range(16):
            for xx in range(16):
                v = px[yy][xx]
                if v:
                    dr.rectangle([(x + xx) * scale, (2 + yy) * scale, (x + xx + 1) * scale - 1,
                                  (2 + yy + 1) * scale - 1], fill=pal[v])
        x += adv
    im.save(out)


def sheet(pac, out, first=0, count=1024, scale=2):
    cols = 16
    cw, ch = 16 * scale + 4, 16 * scale + 12
    nrows = (count + cols - 1) // cols
    im = Image.new('RGB', (cols * cw + 40, nrows * ch), (40, 40, 60))
    dr = ImageDraw.Draw(im)
    # value bit 0 = glyph body, bit 1 = drop shadow; body-only reads cleaner for transcription
    pal = [(0, 0, 0), (70, 70, 70), (255, 255, 255), (255, 255, 255)]
    for i in range(count):
        g = first + i
        cx, cy = 40 + (i % cols) * cw, (i // cols) * ch
        if i % cols == 0:
            dr.text((2, cy + 10), '%03X' % g, fill=(255, 255, 0))
        dr.text((cx, cy), '%X' % (g & 15), fill=(120, 200, 255))
        gl = glyph(pac, g)
        for y in range(16):
            for x in range(16):
                dr.rectangle([cx + x * scale, cy + 10 + y * scale, cx + x * scale + scale - 1,
                              cy + 10 + y * scale + scale - 1], fill=pal[gl[y][x]])
    im.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['sheet'])
    ap.add_argument('pac')
    ap.add_argument('out')
    ap.add_argument('--first', type=lambda s: int(s, 0), default=0)
    ap.add_argument('--count', type=lambda s: int(s, 0), default=1024)
    ap.add_argument('--scale', type=int, default=2)
    a = ap.parse_args()
    pac = open(a.pac, 'rb').read()
    sheet(pac, a.out, a.first, a.count, a.scale)


if __name__ == '__main__':
    main()
