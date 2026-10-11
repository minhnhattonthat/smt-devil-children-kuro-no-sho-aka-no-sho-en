"""Event overlay (B_EVENT/R_EVENT.BIN) message map: pointer slots -> messages.

Messages are 16-bit text ending in FFFF, 4-aligned, referenced by absolute 32-bit pointers (4-aligned slots)
in the event bytecode. Load address 0x80170000 for both overlays (checked for B in RAM).

  python -X utf8 tools/events.py stats
"""
import collections
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import text  # noqa: E402

BASE = 0x80170000


def message_len(d, off):
    """Bytes of a message at off (through FFFF), or 0 if it is not text-like."""
    p, glyphs = off, 0
    while p + 2 <= len(d) and p - off < 4000:
        v = struct.unpack_from('<H', d, p)[0]
        p += 2
        if v == 0xFFFF:
            return p - off if glyphs else 0
        if v in text.CTRL:
            p += 2 * text.CTRL[v][1]
        elif v < text.NGLYPH:
            glyphs += 1
        else:
            return 0
    return 0


def is_dialogue(d, off):
    """Pointer targets include numeric data that decodes as 1-3 glyphs ('D', '間', '■　D'): reject those."""
    units = [struct.unpack_from('<H', d, p)[0] for p in range(off, off + message_len(d, off), 2)]
    if 0xFFF3 in units:
        return True
    glyphs = [u for u in units if u < text.NGLYPH and u != 0]
    latin = any(0x23 <= u <= 0x56 for u in glyphs)
    kana = any(0x57 <= u <= 0xFD for u in glyphs)
    return len(glyphs) >= 2 and kana and not latin


def messages(d, base=BASE):
    """{offset: (length, [slot offsets])} for every pointed-to text message."""
    slots = collections.defaultdict(list)
    end = base + len(d)
    for o in range(0, len(d) - 3, 4):
        w = struct.unpack_from('<I', d, o)[0]
        if base <= w < end and not w & 3:
            slots[w - base].append(o)
    out = {}
    for t, sl in slots.items():
        n = message_len(d, t)
        if n and is_dialogue(d, t):
            out[t] = (n, sl)
    return out


def regions(d, msgs):
    """Free space after lifting every message out: merged [start, end) spans incl. zero alignment padding."""
    spans = []
    for off, (n, _) in sorted(msgs.items()):
        end = off + n
        while end % 4 and end < len(d) and d[end] == 0:
            end += 1
        spans.append([off, end])
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged


def repack(d, msgs, new_bytes, base=BASE):
    """Rewrite messages into the freed regions. new_bytes: {orig offset: bytes}. Returns (bytearray, stats).

    Identical byte strings share one copy; every pointer slot of a message is repointed. Raises if it doesn't fit."""
    out = bytearray(d)
    free = regions(d, msgs)
    for s, e in free:
        out[s:e] = bytes(e - s)
    placed = {}
    ri, cur = 0, free[0][0]
    used = 0
    for off in sorted(msgs):
        b = new_bytes[off]
        if b not in placed:
            n = (len(b) + 3) & ~3
            while ri < len(free) and cur + n > free[ri][1]:
                ri += 1
                if ri < len(free):
                    cur = free[ri][0]
            if ri >= len(free):
                raise ValueError('event text does not fit: out of space at message %05X' % off)
            out[cur:cur + len(b)] = b
            placed[b] = cur
            cur += n
            used += n
        for slot in msgs[off][1]:
            struct.pack_into('<I', out, slot, base + placed[b])
    cap = sum(e - s for s, e in free)
    return out, {'used': used, 'capacity': cap}


def main():
    tree = Path(__file__).resolve().parent.parent / 'work' / 'orig' / 'tree'
    b = (tree / 'B_EVENT.BIN').read_bytes()
    r = (tree / 'R_EVENT.BIN').read_bytes()
    mb, mr = messages(b), messages(r)
    tb = collections.Counter(text.decode(b, o)[0] for o in mb)
    tr = collections.Counter(text.decode(r, o)[0] for o in mr)
    print('B msgs %d unique %d | R msgs %d unique %d' % (len(mb), len(tb), len(mr), len(tr)))
    shared = set(tb) & set(tr)
    print('shared texts %d; B-only %d; R-only %d' % (len(shared), len(set(tb) - shared), len(set(tr) - shared)))
    gl = lambda s: sum(1 for c in s if c not in '{}')  # rough
    print('glyph volume: unique-all %d' % sum(len(t) for t in set(tb) | set(tr)))


if __name__ == '__main__':
    main()
