"""Package a release: xdelta3 patch (against the Redump .bin) + README.txt, zipped. Local only; publishing is the user's call.

  python -X utf8 tools/release.py 1.0        -> release/DevilChildren_BlackRed_EN_v1.0.zip

Run after build.py. Stops unless the dump matches rom.sha1, every QA sheet has a verdict (qa_gate.py check) and the
patch re-applied to the clean .bin gives build/dc_en.bin byte for byte."""
import hashlib
import os
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_rom  # noqa: E402

ORIG = ROOT / 'rom/Shin Megami Tensei - Devil Children - Kuro no Sho, Aka no Sho (Japan).bin'
BUILT = ROOT / 'build/dc_en.bin'
OUT = ROOT / 'release'
QA_GATE = (Path(os.environ['SKILL']) if os.environ.get('SKILL') else max(
    (Path.home() / '.claude/plugins/cache/retro-translation/translate-retro-game').glob('*/skills/translate-retro-game'),
    key=lambda p: p.stat().st_mtime)) / 'scripts/qa_gate.py'

README = """Shin Megami Tensei: Devil Children Black Book / Red Book - English translation v{ver}
=====================================================================================

Unofficial fan translation of Shin Megami Tensei: Devil Children Kuro no Sho / Aka no Sho
(PlayStation, Atlus, 2000). Both books and the Webnet disc mode are in English: dialogue, menus,
battles, demon data, the password screen, title and menu graphics.

This is a patch only. It contains no game data; you need your own dump of the Japanese disc.

Base disc (Redump 62163)
------------------------
  Shin Megami Tensei - Devil Children - Kuro no Sho, Aka no Sho (Japan).bin
  Size   {size} bytes
  CRC32  {crc}
  MD5    {md5}
  SHA-1  {sha1}
Other dumps (a different revision, a merged/converted image, an already-patched copy) will not work.

Patched .bin
  CRC32  {pcrc}
  SHA-1  {psha1}

How to patch
------------
1. Apply {patch} to the .bin with xdelta3 (or a front end such as Delta Patcher / xdelta UI):
     xdelta3 -d -s "<original>.bin" {patch} "Devil Children EN.bin"
2. Copy the original .cue, rename it to match the new .bin, and change the FILE line inside it to the new
   .bin name (for example: FILE "Devil Children EN.bin" BINARY).
3. Open the .cue in your emulator.

Tested in PCSX-Redux and DuckStation. Start from a cold boot; savestates made with another build keep the old
text and font in memory.

Passwords
---------
Passwords are English: type them as one word with no spaces (for example HOLYCHILDREN). The full list is in
the project README.

Known issues
------------
- A few lines the original game never shows (cut text with no pointer to it) stay in Japanese on the disc.
- Report bugs at https://github.com/minhnhattonthat/smt-devil-children-kuro-no-sho-aka-no-sho/issues
  (a savestate helps most).

Credits
-------
Translation, tools and engine work: minhnhattonthat, with AI assistance (Claude, Anthropic) for translation
drafts, reverse engineering and tooling.
cj_iwakura's earlier menu proto patch was used as a reference.
Shin Megami Tensei and Devil Children are trademarks of Atlus/SEGA. This is an unofficial fan project; it is not
affiliated with or endorsed by them. Do not distribute pre-patched images.
"""


def digest(path, algo):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, algo).hexdigest()


def crc32(path):
    c = 0
    with open(path, 'rb') as f:
        while b := f.read(1 << 20):
            c = zlib.crc32(b, c)
    return '%08x' % c


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ver = sys.argv[1]
    check_rom.check()
    if subprocess.run([sys.executable, '-X', 'utf8', str(QA_GATE), 'check', str(ROOT / 'work/qa/manifest.tsv'),
                       str(ROOT / 'work/qa/verdicts')]).returncode:
        sys.exit('QA gate not passed: every tour sheet needs an ok/fixed verdict (references/emulator-qa.md)')
    OUT.mkdir(exist_ok=True)
    patch = OUT / f'DevilChildren_BlackRed_EN_v{ver}.xdelta'
    subprocess.run(['xdelta3', '-e', '-9', '-f', '-s', str(ORIG), str(BUILT), str(patch)], check=True)
    back = OUT / 'reapplied.bin'
    subprocess.run(['xdelta3', '-d', '-f', '-s', str(ORIG), str(patch), str(back)], check=True)
    ok = digest(back, 'sha1') == digest(BUILT, 'sha1')
    back.unlink()
    if not ok:
        sys.exit('re-applied patch does not match build/dc_en.bin')
    text = README.format(ver=ver, size=ORIG.stat().st_size, crc=crc32(ORIG), md5=digest(ORIG, 'md5'),
                         sha1=digest(ORIG, 'sha1'), pcrc=crc32(BUILT), psha1=digest(BUILT, 'sha1'), patch=patch.name)
    zpath = OUT / f'DevilChildren_BlackRed_EN_v{ver}.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_STORED) as z:  # xdelta is already compressed
        z.write(patch, patch.name)
        z.writestr('README.txt', text.replace('\n', '\r\n'))
    print('%s (%d bytes): %s + README.txt, re-apply verified' % (zpath, zpath.stat().st_size, patch.name))


if __name__ == '__main__':
    main()
