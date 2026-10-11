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


ARMIPS = ROOT / 'tools' / 'armips' / 'armips.exe'
SPIKE = {  # engine spike: one byte-mode message in place (B_EVENT offset -> English)
    0x3B6CC: '{voice:0003}Find the Norn Key!{wait}{page}{voice:0004}Get that key and bring it{n}'
             'to me! The quick brown fox jumps.{wait}{end}',
}


def build_font(files):
    import font
    pac = bytearray((TREE / 'DEVIL.PAC').read_bytes())
    glyphs = font.load_en(ROOT / 'font' / 'en16.txt')
    widths = bytearray(256)
    for code, (px, adv) in glyphs.items():
        font.put_glyph(pac, code, px)
        widths[code - 0x100] = adv
    (files / 'DEVIL.PAC').write_bytes(pac)
    (BUILD / 'en_width.bin').write_bytes(widths)


def build_exe(files, name):
    shutil.copy(TREE / name, files / name)
    r = subprocess.run([str(ARMIPS), str(ROOT / 'asm' / 'main.asm'), '-strequ', 'EXE', str(files / name),
                        '-strequ', 'WIDTHS', str(BUILD / 'en_width.bin')], capture_output=True, text=True)
    if r.returncode:
        sys.exit('armips failed:\n' + r.stdout + r.stderr)


def build_event(files, name):
    import text
    d = bytearray((TREE / name).read_bytes())
    for off, en in SPIKE.items():
        n = text.decode(d, off)[1]
        b = text.encode_en8(en)
        assert len(b) <= n, (hex(off), len(b), n)
        d[off:off + n] = b + bytes(n - len(b))
    (files / name).write_bytes(d)


def build():
    sys.path.insert(0, str(ROOT / 'tools'))
    files = BUILD / 'files'
    if files.exists():
        shutil.rmtree(files)
    files.mkdir(parents=True)
    build_font(files)
    build_exe(files, 'B_MAIN.EXE')
    build_event(files, 'B_EVENT.BIN')
    overrides = {p.name: p for p in files.iterdir()}
    make_disc(overrides, BUILD / 'dc_en.bin')
    print('built', BUILD / 'dc_en.bin')
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    sys.exit({'dump': lambda: dump() or 0, 'identity': identity, 'build': build}[cmd]())
