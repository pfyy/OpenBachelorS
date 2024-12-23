def is_char_id(char_id: str) -> bool:
    return char_id.startswith("char_")


def get_char_num_id(char_id: str) -> int:
    return int(char_id.split("_")[1])
