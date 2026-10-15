"""Screen tour: land on every scene from a field savestate, shoot it, build captioned contact sheets.

  python -X utf8 tools/debug/tour.py regen [--book B|R]     cold-boot the current build to the field -> work/states/field_<book>.sstate
  python -X utf8 tools/debug/tour.py list
  python -X utf8 tools/debug/tour.py run [NAME|GROUP ...] [--jobs 3] [--disc build/dc_en.cue]
Output work/qa/tour/<name>/sNN.png and work/qa/tour/sheet_<group>.png (one tile per `shot`).
Re-run `regen` after every build that changes code, font or graphics: savestates keep the old RAM and VRAM.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from scenes import SCENES, BOOKS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EMU = ROOT / '.claude/skills/translate-retro-game/scripts/emu.py'
BIOS = ROOT / 'tools/pcsx-redux/bios/SCPH-5500.bin'
OUT = ROOT / 'work/qa/tour'
SUF = ''  # '_jp' with --jp: the original disc, for a side-by-side with the English build
JP_CUE = 'rom/Shin Megami Tensei - Devil Children - Kuro no Sho, Aka no Sho (Japan).cue'
def lua_steps(steps):
    """Scene steps -> a Lua list literal for tools/debug/scene.lua."""
    return '{' + ','.join("'" + x + "'" for x in steps) + '}'


def emu(cue, out, extra, book):
    cmd = [sys.executable, '-X', 'utf8', str(EMU), str(cue), '--out', str(out), '--bios', str(BIOS)] + extra
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=900)
    return r


def run_scene(name, cue, book):
    sc = SCENES[name]
    d = OUT / name
    d.mkdir(parents=True, exist_ok=True)
    for p in d.glob('*.png'):
        p.unlink()
    extra = ['--state-in', str(ROOT / f'work/states/field_{book}{SUF}.sstate'), '--frames', str(sc.get('max', 12000)),
             '--script', str(ROOT / 'tools/debug/scene.lua'), '--var', 'STEPS=' + lua_steps(sc['steps'])]
    if 'call' in sc:
        fn, *args = sc['call']
        extra += ['--script', str(ROOT / 'tools/debug/warp.lua'), '--var', f'FN={fn:#x}', '--var', 'AT=10']
        extra += [x for i, a in enumerate(args) for x in ('--var', f'A{i}={a:#x}')]
        if sc.get('poke'):
            extra += ['--var', 'POKE={' + ','.join(f'[{a:#x}]={v}' for a, v in sc['poke'].items()) + '}']
    r = emu(cue, d, extra, book)
    got = sorted(d.glob('s[0-9]*.png'))
    ok = r.returncode == 0 and len(got) == sc['steps'].count('shot')
    return name, ok, len(got), (r.stdout + r.stderr)[-300:]


def sheet(group, names):
    tiles = []
    for n in names:
        for p in sorted((OUT / n).glob('s*.png')):
            im = Image.open(p).convert('RGB')
            im = im.resize((256, 240), Image.LANCZOS) if im.width != 256 else im
            t = Image.new('RGB', (256, 254), (40, 0, 40))
            t.paste(im, (0, 14))
            ImageDraw.Draw(t).text((2, 1), f'{n} {p.stem}', fill=(255, 255, 0))
            tiles.append(t)
    cols = 4
    for k in range(0, len(tiles), 12):  # 12 tiles per sheet keeps the text readable
        part = tiles[k:k + 12]
        rows = (len(part) + cols - 1) // cols
        im = Image.new('RGB', (cols * 256, rows * 254), (40, 0, 40))
        for i, t in enumerate(part):
            im.paste(t, ((i % cols) * 256, (i // cols) * 254))
        out = OUT / f'sheet_{group}_{k // 12}.png'
        im.save(out)
        print(out)


def regen(book):
    disc = ROOT / (JP_CUE if SUF else 'build/dc_en.cue')
    route = ROOT / ('tools/routes/load_save.txt' if book == 'B' else 'tools/routes/load_save_red.txt')
    card = ROOT / BOOKS[book]['card']
    out = ROOT / 'work/qa/mkstate'
    r = emu(disc, out, ['--memcard', str(card), '--route', str(route),
                        '--state-out', str(ROOT / f'work/states/field_{book}{SUF}.sstate')], book)
    print(r.stdout[-300:], r.stderr[-300:])
    return r.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('cmd', choices=['regen', 'list', 'run'])
    ap.add_argument('names', nargs='*')
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--book', default='B')
    ap.add_argument('--jp', action='store_true', help='original Japanese disc: work/qa/tour_jp, states field_*_jp')
    a = ap.parse_args()
    global OUT, SUF
    if a.jp:
        OUT, SUF = ROOT / 'work/qa/tour_jp', '_jp'
    if a.cmd == 'regen':
        return regen(a.book)
    if a.cmd == 'list':
        for n, s in SCENES.items():
            print(f"{s['group']:8} {n:16} {s.get('note', '')}")
        return 0
    sel = [n for n, s in SCENES.items() if not a.names or n in a.names or s['group'] in a.names]
    cue = ROOT / (JP_CUE if a.jp else 'build/dc_en.cue')
    bad = 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for name, ok, n, tail in ex.map(lambda n: run_scene(n, cue, a.book), sel):
            print(('ok  ' if ok else 'FAIL'), name, n, '' if ok else tail)
            bad += not ok
    for g in dict.fromkeys(SCENES[n]['group'] for n in sel):
        sheet(g, [n for n in sel if SCENES[n]['group'] == g])
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
