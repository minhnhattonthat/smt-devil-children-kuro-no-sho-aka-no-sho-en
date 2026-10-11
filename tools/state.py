"""PCSX-Redux savestate helpers (uncompressed protobuf; main RAM 2 MiB at offset 0x27).

  python -X utf8 tools/state.py ram STATE OUT.ram       write the 2 MiB RAM image
  python -X utf8 tools/state.py find STATE JPTEXT       RAM addresses of a JP string (encoded with tbl/jp.tbl)
"""
import sys
from pathlib import Path

RAM_OFF = 0x27  # checked against B_MAIN.EXE code at three offsets
RAM_SIZE = 0x200000


def ram(path):
    return Path(path).read_bytes()[RAM_OFF:RAM_OFF + RAM_SIZE]


def main():
    cmd, path = sys.argv[1], sys.argv[2]
    r = ram(path)
    if cmd == 'ram':
        Path(sys.argv[3]).write_bytes(r)
    elif cmd == 'find':
        sys.path.insert(0, str(Path(__file__).parent))
        import text
        e = text.encode(sys.argv[3])
        i = r.find(e)
        while i >= 0:
            print('%08X' % (0x80000000 + i))
            i = r.find(e, i + 1)


if __name__ == '__main__':
    main()
