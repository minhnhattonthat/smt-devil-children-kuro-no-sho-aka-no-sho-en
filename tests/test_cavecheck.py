import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import cavecheck  # noqa: E402


def code(*words):
    return b''.join(struct.pack('<I', w) for w in words)


def lui(rt, hi):
    return 0x3C000000 | rt << 16 | hi


def sw(rt, rs, imm):
    return 0xAC000000 | rs << 21 | rt << 16 | imm & 0xFFFF


def test_scan_flags_store_into_cave(tmp_path):
    p = tmp_path / 'a.bin'
    p.write_bytes(code(lui(2, 0x800D), sw(3, 2, 0x1BB0)))
    hits = cavecheck.scan(p, [('CAVE3', 0x800D1BA4, 0x800D1D84)])
    assert [(h[1], h[3]) for h in hits] == [(0x800D1BB0, 'FAIL')]


def test_scan_ignores_other_path_after_jump(tmp_path):
    p = tmp_path / 'a.bin'
    j = 0x08000000
    p.write_bytes(code(lui(2, 0x800D), j, 0, sw(3, 2, 0x1BB0)))  # the sw is on another path, v0 not live there
    assert cavecheck.scan(p, [('CAVE3', 0x800D1BA4, 0x800D1D84)]) == []
