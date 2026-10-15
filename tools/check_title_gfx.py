"""Validate title-only changes against a saved pre-edit gfx.py preview.

python -X utf8 tools/check_title_gfx.py work/qa/logos/before_textures \
    --vram work/qa/logos/before/main.vram.bin

The optional VRAM dump must be from the ORIGINAL cold_title screen. This
checks the source identification, write boundaries, copyright and menu pixels.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageChops

import gfx
import tim


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('before', type=Path)
    ap.add_argument('--vram', type=Path)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    original = (root / 'work/orig/tree/DEVIL.PAC').read_bytes()
    edited = bytearray(original)
    gfx.apply(edited)
    for off, name in [(0x156A220, 'main'), (0x15B7000, 'black'), (0x15C7800, 'red')]:
        source = tim.parse(original, off)
        result = tim.parse(edited, off)
        before = tim.to_image(source) if name == 'main' else Image.open(args.before / f'{off:08X}.png')
        after = tim.to_image(result)
        diff = ImageChops.difference(before, after)
        print(name, 'changed RGB bbox:', diff.getbbox())
        assert diff.crop((0, 175, 256, 256)).getbbox() is None, name
        data_start = source['end'] - len(source['data'])
        assert original[off:data_start] == edited[off:data_start], 'TIM header/CLUT changed'
        if name == 'main':
            for y in range(256):
                for x in range(256):
                    if not (20 <= x < 237 and 32 <= y < 174):
                        i = y * 256 + x
                        assert source['data'][i] == result['data'][i], (x, y)
            if args.vram:
                vram = args.vram.read_bytes()
                for y in (64, 128):
                    assert vram[y * 2048 + 1024:y * 2048 + 1280] == source['data'][y * 256:(y + 1) * 256]
                print('Main title source confirmed by exact VRAM rows at (512, 64/128).')
    for off in (0x1586800, 0x1596A20, 0x15A6C40):
        before = Image.open(args.before / f'{off:08X}.png')
        after = tim.to_image(tim.parse(edited, off))
        assert ImageChops.difference(before, after).getbbox() is None
    print('Copyright, Start sprite, menu options and book selection unchanged.')


if __name__ == '__main__':
    main()
