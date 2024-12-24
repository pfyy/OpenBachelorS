import os
import json


def is_char_id(char_id: str) -> bool:
    return char_id.startswith("char_")


def get_char_num_id(char_id: str) -> int:
    return int(char_id.split("_")[1])


def merge_delta_into_tmpl(tmpl: dict, modified: dict, deleted: dict):
    stk = []
    stk.append(
        (
            tmpl,
            modified,
        )
    )
    while len(stk):
        (
            cur_tmpl,
            cur_modified,
        ) = stk.pop()
        for key in cur_modified:
            value = cur_modified[key]

            if isinstance(value, dict):
                if key not in cur_tmpl or not isinstance(cur_tmpl[key], dict):
                    cur_tmpl[key] = {}
                next_tmpl = cur_tmpl[key]
                stk.append((next_tmpl, value))
            else:
                cur_tmpl[key] = value

    stk = []
    stk.append(
        (
            tmpl,
            deleted,
        )
    )
    while len(stk):
        (
            cur_tmpl,
            cur_deleted,
        ) = stk.pop()
        for key in cur_deleted:
            value = cur_deleted[key]
            if isinstance(value, dict):
                if key in cur_tmpl:
                    next_tmpl = cur_tmpl[key]
                    stk.append((next_tmpl, value))
            else:
                for deleted_key in value:
                    cur_tmpl[key].pop(deleted_key, None)


def load_delta_json_obj(path: str):
    if not os.path.isfile(path):
        return {"modified": {}, "deleted": {}}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_delta_json_obj(path: str, modified: dict, deleted: dict):
    dirpath = os.path.dirname(dirpath)
    os.makedirs(dirpath, exist_ok=True)
    json_obj = {"modified": modified, "deleted": deleted}
    with open(path, "w", encoding="utf-8") as f:
        return json.dump(json_obj, f, indent=4, ensure_ascii=False)
