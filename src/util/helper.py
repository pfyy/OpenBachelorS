import os
import json


def is_char_id(char_id: str) -> bool:
    return char_id.startswith("char_")


def get_char_num_id(char_id: str) -> int:
    return int(char_id.split("_")[1])


def load_delta_json_obj(path: str):
    if not os.path.isfile(path):
        return {"modified": {}, "deleted": {}}
    with open(path, encoding="utf-8") as f:
        return json.load(f)
