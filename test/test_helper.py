from openbachelors.util.helper import validate_is_cheat


def test_validate_is_cheat():
    assert validate_is_cheat(
        "Nzc3Nzc3Nzc0Nzc3NzQ3Nzc3NDc3Nzc0Nzc3Nzc3Nzc3Nzc3",
        "00000000-0000-0000-0000-000000000000",
    )
