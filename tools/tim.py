"""PS1 TIM images inside a file (e.g. DEVIL.PAC).

  python -X utf8 tools/tim.py list FILE                 offsets, bpp, size, VRAM position
  python -X utf8 tools/tim.py png FILE OFF OUT.png [--clut N]
"""
import struct
import sys

from PIL import Image


def parse(d, o):
    """Return dict for a TIM at o, or None."""
    if d[o:o + 4] != b'\x10\0\0\0':
        return None
    fl = struct.unpack_from('<I', d, o + 4)[0]
    if fl & ~0xF or (fl & 7) > 3:
        return None
    p = o + 8
    t = {'off': o, 'bpp': [4, 8, 16, 24][fl & 3], 'clut': None}
    try:
        if fl & 8:
            ln, x, y, w, h = struct.unpack_from('<IHHHH', d, p)
            if ln != 12 + w * h * 2 or not w or not h:
                return None
            t['clut'] = (x, y, w, h, d[p + 12:p + ln])
            p += ln
        ln, x, y, w, h = struct.unpack_from('<IHHHH', d, p)
        if ln != 12 + w * h * 2 or not w or not h or w > 1024 or h > 512:
            return None
    except struct.error:
        return None
    t.update(x=x, y=y, w=w, h=h, data=d[p + 12:p + ln], end=p + ln, pw=w * 16 // t['bpp'])
    return t


def scan(d, align=4):
    o = 0
    while o < len(d) - 32:
        t = parse(d, o)
        if t:
            yield t
            o = t['end']
            o += -o % align
        else:
            o += align


def rgb(c):
    return ((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3)


def to_image(t, clut_row=0):
    im = Image.new('RGB', (t['pw'], t['h']))
    px = im.load()
    d = t['data']
    pal = None
    if t['clut']:
        cw = t['clut'][2]
        cd = t['clut'][4]
        pal = [rgb(struct.unpack_from('<H', cd, (clut_row * cw + i) * 2)[0]) for i in range(cw)]
    for y in range(t['h']):
        for x in range(t['pw']):
            if t['bpp'] == 4:
                b = d[y * t['w'] * 2 + x // 2]
                v = (b >> 4) if x & 1 else b & 15
                px[x, y] = pal[v] if pal else (v * 17,) * 3
            elif t['bpp'] == 8:
                v = d[y * t['w'] * 2 + x]
                px[x, y] = pal[v] if pal else (v,) * 3
            else:
                px[x, y] = rgb(struct.unpack_from('<H', d, (y * t['w'] + x) * 2)[0])
    return im


def main():
    cmd, path = sys.argv[1], sys.argv[2]
    d = open(path, 'rb').read()
    if cmd == 'list':
        for t in scan(d):
            print('%08X %2dbpp %4dx%-3d @%d,%d%s' % (t['off'], t['bpp'], t['pw'], t['h'], t['x'], t['y'],
                                                   ' clut@%d,%d x%d' % t['clut'][:3] if t['clut'] else ''))
    else:
        t = parse(d, int(sys.argv[3], 16))
        clut = int(sys.argv[sys.argv.index('--clut') + 1]) if '--clut' in sys.argv else 0
        to_image(t, clut).save(sys.argv[4])


if __name__ == '__main__':
    main()
