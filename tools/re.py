"""RE helpers for PS-X EXEs and overlays.

  python -X utf8 tools/re.py dis FILE ADDR [COUNT]        disassemble (ADDR = RAM 0x8xxxxxxx or file offset)
  python -X utf8 tools/re.py xref FILE TARGET              find lui/addiu|ori|lw.. pairs and jal that build TARGET
  python -X utf8 tools/re.py find FILE HEX                 find byte pattern, print file offsets + RAM addresses
Overlays (*.BIN) have no header: pass --base 0x8xxxxxxx (RAM address of file offset 0).
"""
import argparse
import struct
import sys

from capstone import CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN, Cs


class Image:
    def __init__(self, path, base=None):
        self.data = open(path, 'rb').read()
        if self.data[:8] == b'PS-X EXE' and base is None:
            self.base = struct.unpack_from('<I', self.data, 0x18)[0] - 0x800
        else:
            self.base = base or 0
        self.path = path

    def off(self, addr):
        return addr - self.base if addr >= 0x80000000 else addr

    def addr(self, off):
        return off + self.base

    def u32(self, off):
        return struct.unpack_from('<I', self.data, off)[0]


def disasm(img, addr, count):
    md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)
    md.skipdata = True  # keep going through data words
    o = img.off(addr)
    for ins in md.disasm(img.data[o:o + count * 4], img.addr(o)):
        print('%08X %06X  %-8s %s' % (ins.address, ins.address - img.base, ins.mnemonic, ins.op_str))


def xref(img, target):
    """Words that point at TARGET directly, jal TARGET, and lui+imm pairs within 16 instructions."""
    d = img.data
    hi, lo = (target + 0x8000) >> 16, target & 0xFFFF
    jal = 0x0C000000 | ((target >> 2) & 0x3FFFFFF)
    for o in range(0, len(d) - 3, 4):
        w = struct.unpack_from('<I', d, o)[0]
        if w == target:
            print('ptr  %06X %08X' % (o, img.addr(o)))
        elif w == jal:
            print('jal  %06X %08X' % (o, img.addr(o)))
        elif w >> 26 == 0x0F and w & 0xFFFF == hi:  # lui rt, hi
            rt = (w >> 16) & 31
            for k in range(1, 17):
                if o + 4 * k + 4 > len(d):
                    break
                w2 = struct.unpack_from('<I', d, o + 4 * k)[0]
                op = w2 >> 26
                if (w2 >> 21) & 31 == rt and op in (0x09, 0x0D, 0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B) \
                        and w2 & 0xFFFF == lo:
                    print('pair %06X %08X  (lo at %06X)' % (o, img.addr(o), o + 4 * k))
                    break


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['dis', 'xref', 'find'])
    ap.add_argument('file')
    ap.add_argument('arg')
    ap.add_argument('count', nargs='?', type=lambda s: int(s, 0), default=32)
    ap.add_argument('--base', type=lambda s: int(s, 0))
    a = ap.parse_args()
    img = Image(a.file, a.base)
    if a.cmd == 'dis':
        disasm(img, int(a.arg, 16), a.count)
    elif a.cmd == 'xref':
        xref(img, int(a.arg, 16))
    else:
        pat = bytes.fromhex(a.arg)
        o = img.data.find(pat)
        while o >= 0:
            print('%06X %08X' % (o, img.addr(o)))
            o = img.data.find(pat, o + 1)


if __name__ == '__main__':
    sys.exit(main())
