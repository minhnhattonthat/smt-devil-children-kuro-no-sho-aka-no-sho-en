import build


def test_identity_rebuild_is_byte_identical():
    assert build.identity() == 0
