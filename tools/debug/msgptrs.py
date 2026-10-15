"""RAM pointers of every dialogue message of the BUILT event overlay: python -X utf8 tools/debug/msgptrs.py [B|R]
Messages are found in the original overlay (kana check works there); each pointer slot in the build holds the
repacked address. Prints `ptr  orig_offset  text` lines (decoded from the build)."""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import events  # noqa: E402
import text  # noqa: E402


def message_ptrs(book='B'):
    name = f'{book}_EVENT.BIN'
    orig = (ROOT / 'work/orig/tree' / name).read_bytes()
    built = (ROOT / 'build/files' / name).read_bytes()
    out = []
    for off, (n, slots) in sorted(events.messages(orig).items()):
        v = struct.unpack_from('<I', built, slots[0])[0]
        out.append((v, off, text.decode_en(built, v - events.BASE)[0] if hasattr(text, 'decode_en') else ''))
    return out


if __name__ == '__main__':
    for v, off, t in message_ptrs(sys.argv[1] if len(sys.argv) > 1 else 'B')[:int(sys.argv[2]) if len(sys.argv) > 2 else None]:
        print('%08X %06X %s' % (v, off, t[:60].replace('\n', ' ')))
