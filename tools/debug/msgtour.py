"""Show every event-overlay dialogue message of the build through the game's own VM and check the rendered pages.

  python -X utf8 tools/debug/msgtour.py [--jobs 4] [--first N --last N] [--book B] [--check-only]
Needs work/states/field_B.sstate from `tour.py regen`. Output work/qa/msgs/: s<id>_<page>.png per page, report.txt, and
sheet_flagged_*.png. A page is flagged when white text pixels reach the box edge (x > 242) or the bottom (y > 220),
or when a message got stuck. Ids: 3000 + index in the overlay message table (0x801BA0F8); see msgs.lua.
"""
import argparse
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
EMU = ROOT / '.claude/skills/translate-retro-game/scripts/emu.py'
BIOS = ROOT / 'tools/pcsx-redux/bios/SCPH-5500.bin'
OUT = ROOT / 'work/qa/msgs'
TABLE = 0x801BA0F8
BASE = 0x80170000


JP = False  # --jp: the original disc (overlay from work/orig/tree, state field_*_jp, output work/qa/msgs_jp)
JP_CUE = 'rom/Shin Megami Tensei - Devil Children - Kuro no Sho, Aka no Sho (Japan).cue'


def message_ids(book):
    d = (ROOT / ('work/orig/tree' if JP else 'build/files') / f'{book}_EVENT.BIN').read_bytes()
    seen, ids = set(), []
    for k in range(2100):
        v = struct.unpack_from('<I', d, TABLE - BASE + 4 * k)[0]
        if BASE <= v < BASE + len(d) and v not in seen:
            seen.add(v)
            ids.append(3000 + k)
    return exe_ids(book) + ids


def exe_ids(book):
    """Ids below 3000 point into B_MAIN's own message table (0x800CECD4): tutorial, shop, bank talk. Only real text."""
    import re
    sys.path.insert(0, str(ROOT / 'tools'))
    import text
    f = {'B': 'B_MAIN.EXE', 'R': 'R_MAIN.EXE'}[book]
    d = (ROOT / 'work/orig/tree' / f).read_bytes()
    shift = 0 if book == 'B' else 0xC  # R_MAIN is B_MAIN - 0xC
    out, seen = [], set()
    for i in range(2400):  # beyond that the table runs into other data
        if i in (521, 536):  # interactive prompts (Yes/No window, a menu loop): the page loop never ends; see tour scenes
            continue
        p = struct.unpack_from('<I', d, 0x800CECD4 - shift - 0x80010000 + 0x800 + 4 * i)[0]
        o = p - 0x80010000 + 0x800
        if not 0x80010000 <= p < 0x80010000 + len(d) - 0x800 or p in seen:
            continue
        t = text.decode(d, o)[0]
        if t.endswith('{end}') and len(re.findall('[ぁ-ヿ一-鿿]', t)) >= 3 and '[' not in t[:6]:
            seen.add(p)
            out.append(i)
    return out


def run_chunk(k, ids, book, out):
    lua = out / f'ids_{k}.lua'
    lua.write_text('IDS={' + ','.join(map(str, ids)) + '}\n')
    cue = ROOT / (JP_CUE if JP else 'build/dc_en.cue')
    cmd = [sys.executable, '-X', 'utf8', str(EMU), str(cue), '--out', str(out / f'c{k}'),
           '--bios', str(BIOS), '--state-in', str(ROOT / f'work/states/field_{book}{"_jp" if JP else ""}.sstate'),
           '--frames', '600000', '--timeout', '3000', '--script', str(ROOT / 'tools/debug/hijack.lua'),
           '--script', str(ROOT / 'tools/debug/jpscan.lua'), '--script', str(lua),
           '--script', str(ROOT / 'tools/debug/msgs.lua'), '--var', "TAG='s'"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=3600)
    return k, r.returncode, (r.stdout + r.stderr)[-200:]


def white_bbox(im):
    px = im.load()
    xs, ys = [], []
    for y in range(148, 238):
        for x in range(8, 250):
            if px[x, y][:3] == (255, 255, 255):
                xs.append(x)
                ys.append(y)
    return (min(xs), max(xs), min(ys), max(ys)) if xs else None


def check(out):
    flagged, pages = [], 0
    for p in sorted(out.glob('c*/s*.png')):
        pages += 1
        if 'stuck' in p.name:
            flagged.append((p, 'stuck'))
            continue
        bb = white_bbox(Image.open(p).convert('RGB'))
        if bb and (bb[1] > 242 or bb[3] > 220):  # legit text tops out at x 238, y 214 (option lists)
            flagged.append((p, f'text reaches x={bb[1]} y={bb[3]}'))
    lines = [f'{pages} pages, {len(flagged)} flagged'] + [f'{p.parent.name}/{p.name}  {why}' for p, why in flagged]
    (out / 'report.txt').write_text('\n'.join(lines) + '\n')
    for k in range(0, len(flagged), 12):
        part = flagged[k:k + 12]
        sheet = Image.new('RGB', (4 * 256, ((len(part) + 3) // 4) * 254), (40, 0, 40))
        for i, (p, why) in enumerate(part):
            t = Image.new('RGB', (256, 254), (40, 0, 40))
            t.paste(Image.open(p).convert('RGB'), (0, 14))
            ImageDraw.Draw(t).text((2, 1), p.stem, fill=(255, 255, 0))
            sheet.paste(t, ((i % 4) * 256, (i // 4) * 254))
        sheet.save(out / f'sheet_flagged_{k // 12}.png')
    print('\n'.join(lines[:30]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--book', default='B')
    ap.add_argument('--chunk', type=int, default=120, help='messages per emulator run')
    ap.add_argument('--first', type=int, default=1)
    ap.add_argument('--last', type=int)
    ap.add_argument('--check-only', action='store_true')
    ap.add_argument('--ids', help='comma-separated message ids instead of all')
    ap.add_argument('--jp', action='store_true', help='the original Japanese disc, for comparison')
    a = ap.parse_args()
    global OUT, JP
    if a.jp:
        OUT, JP = ROOT / 'work/qa/msgs_jp', True
    if not a.check_only:
        ids = [int(x) for x in a.ids.split(',')] if a.ids else message_ids(a.book)[a.first - 1:a.last]
        OUT.mkdir(parents=True, exist_ok=True)
        n = a.chunk  # the emulator's Lua dies ('stack overflow') after ~175 hijacked calls: restart often
        chunks = [ids[i:i + n] for i in range(0, len(ids), n)]
        with ThreadPoolExecutor(a.jobs) as ex:
            for k, rc, tail in ex.map(lambda kv: run_chunk(kv[0], kv[1], a.book, OUT), enumerate(chunks)):
                print('chunk', k, 'exit', rc, tail.strip().splitlines()[-1:] if tail.strip() else '')
    check(OUT)


if __name__ == '__main__':
    main()
