"""Build entry point.

  python -X utf8 build.py            build build/dc_en.bin + .cue from rom/ + translations
  python -X utf8 build.py dump       unpack the original disc to work/orig (once)
  python -X utf8 build.py identity   rebuild the untouched disc and compare SHA-1 with the original
"""
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROM_CUE = ROOT / 'rom' / 'Shin Megami Tensei - Devil Children - Kuro no Sho, Aka no Sho (Japan).cue'
ORIG = ROOT / 'work' / 'orig'
TREE = ORIG / 'tree'
BUILD = ROOT / 'build'
MKPSXISO = ROOT / 'tools' / 'mkpsxiso-2.30-win64'
ORIG_SHA1 = 'f7a3e476f595e656d5d5788a27aa6beec504a5bc'


def dump():
    if (ORIG / 'layout.xml').exists():
        return
    ORIG.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(MKPSXISO / 'dumpsxiso.exe'), '-x', str(TREE), '-s', str(ORIG / 'layout.xml'), str(ROM_CUE)],
                   check=True, capture_output=True)


def make_disc(overrides, out_bin):
    """overrides: disc file name -> path of replacement file. Unchanged files are read from work/orig/tree."""
    dump()
    xml = (ORIG / 'layout.xml').read_text(encoding='utf-8')

    def src(m):
        name = m[1]
        p = overrides.get(name.rstrip('.'), TREE / name.rstrip('.'))
        return '<file name="%s" source="%s"' % (name, Path(p).as_posix())
    xml = re.sub(r'<file name="([^"]+)"', src, xml)
    xml = xml.replace('file="tree/license_data.dat"', 'file="%s"' % (TREE / 'license_data.dat').as_posix())
    xml = xml.replace('source="tree"', 'source="%s"' % TREE.as_posix())
    out_bin = Path(out_bin)
    out_bin.parent.mkdir(parents=True, exist_ok=True)
    lay = out_bin.with_suffix('.xml')
    lay.write_text(xml, encoding='utf-8')
    r = subprocess.run([str(MKPSXISO / 'mkpsxiso.exe'), '-y', '-q', '-o', str(out_bin), '-c',
                        str(out_bin.with_suffix('.cue')), str(lay)], capture_output=True, text=True)
    if r.returncode:
        sys.exit('mkpsxiso failed:\n' + r.stdout + r.stderr)
    # mkpsxiso writes the bin's full path into the cue; make it relative so the pair can move
    cue = out_bin.with_suffix('.cue')
    cue.write_text(re.sub(r'FILE "[^"]*"', 'FILE "%s"' % out_bin.name, cue.read_text()), encoding='utf-8')


def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def identity():
    out = ROOT / 'work' / 'ident' / 'ident.bin'
    make_disc({}, out)
    ok = sha1(out) == ORIG_SHA1
    print('identity', 'OK' if ok else 'MISMATCH')
    return 0 if ok else 1


def build():
    sys.path.insert(0, str(ROOT / 'tools'))
    files = BUILD / 'files'
    if files.exists():
        shutil.rmtree(files)
    files.mkdir(parents=True)
    overrides = {}
    # build steps register patched copies of disc files here (name -> path under build/files)
    make_disc(overrides, BUILD / 'dc_en.bin')
    print('built', BUILD / 'dc_en.bin')
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    sys.exit({'dump': lambda: dump() or 0, 'identity': identity, 'build': build}[cmd]())
