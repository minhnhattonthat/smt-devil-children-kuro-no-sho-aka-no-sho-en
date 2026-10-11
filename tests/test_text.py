import text
from build import TREE


def test_table_covers_all_glyph_slots():
    assert len(text.JP) == 0x2DE  # 0x000-0x2DF minus the two icon slots 0x0FE/0x0FF


def test_scan_roundtrip_exe_and_event():
    for name in ('B_MAIN.EXE', 'B_EVENT.BIN', 'B_BATTLE.BIN'):
        data = (TREE / name).read_bytes()
        n = 0
        for off, ln, t in text.scan(data):
            assert text.encode(t) == data[off:off + ln], (name, hex(off), t)
            n += 1
        assert n > 50, name
