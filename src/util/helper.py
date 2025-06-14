import os
import json
from base64 import urlsafe_b64encode, urlsafe_b64decode
from base64 import b64encode, b64decode
import io
import zipfile
import subprocess
from uuid import uuid4
import re
from hashlib import md5
import random

from pathvalidate import is_valid_filename
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from ..const.filepath import TMP_DIRPATH


def is_char_id(char_id: str) -> bool:
    return char_id.startswith("char_")


def get_char_num_id(char_id: str) -> int:
    return int(char_id.split("_")[1])


def get_char_id_from_skin_id(skin_id: str) -> str:
    return skin_id.partition("@")[0].partition("#")[0]


def get_username_by_token(token: str) -> str:
    return urlsafe_b64encode(token.encode()).decode()[:64]


def encode_stage_id(stage_id: str) -> str:
    return urlsafe_b64encode(stage_id.encode()).decode()


def decode_stage_id(stage_id: str) -> str:
    return urlsafe_b64decode(stage_id.encode()).decode()


def encode_battle_replay(decoded_battle_replay: dict) -> str:
    bytes_io = io.BytesIO()
    with zipfile.ZipFile(bytes_io, "w") as zip_file:
        zip_file.writestr("default_entry", json.dumps(decoded_battle_replay))
    battle_replay = b64encode(bytes_io.getvalue()).decode()
    return battle_replay


def decode_battle_replay(battle_replay: str) -> dict:
    bytes_io = io.BytesIO(b64decode(battle_replay.encode()))
    with zipfile.ZipFile(bytes_io) as zip_file:
        decoded_battle_replay = json.loads(zip_file.read("default_entry"))
    return decoded_battle_replay


def load_battle_replay_from_file(battle_replay_filepath: str) -> str:
    with open(battle_replay_filepath, encoding="utf-8") as f:
        decoded_battle_replay = json.load(f)
    battle_replay = encode_battle_replay(decoded_battle_replay)
    return battle_replay


def save_battle_replay_to_file(battle_replay_filepath: str, battle_replay: str):
    decoded_battle_replay = decode_battle_replay(battle_replay)
    with open(battle_replay_filepath, "w", encoding="utf-8") as f:
        json.dump(decoded_battle_replay, f, indent=4, ensure_ascii=False)


ASSIST_LST_IDX_UID_OFFSET = 10000


def get_friend_uid_from_assist_lst_idx(assist_lst_idx: int) -> str:
    return str(assist_lst_idx + ASSIST_LST_IDX_UID_OFFSET)


def get_assist_lst_idx_from_friend_uid(friend_uid: str):
    return int(friend_uid) - ASSIST_LST_IDX_UID_OFFSET


def convert_char_obj_to_assist_char_obj(char_obj: dict):
    if "skin" in char_obj:
        char_obj["skinId"] = char_obj["skin"]
        del char_obj["skin"]
    if "defaultSkillIndex" in char_obj:
        char_obj["skillIndex"] = char_obj["defaultSkillIndex"]
        del char_obj["defaultSkillIndex"]
    if "tmpl" in char_obj:
        for i in char_obj["tmpl"]:
            if "defaultSkillIndex" in char_obj["tmpl"][i]:
                char_obj["tmpl"][i]["skillIndex"] = char_obj["tmpl"][i][
                    "defaultSkillIndex"
                ]
                del char_obj["tmpl"][i]["defaultSkillIndex"]


def load_delta_json_obj(path: str):
    if not os.path.isfile(path):
        return {"modified": {}, "deleted": {}}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_delta_json_obj(path: str, modified: dict, deleted: dict):
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath, exist_ok=True)
    json_obj = {"modified": modified, "deleted": deleted}
    with open(path, "w", encoding="utf-8") as f:
        return json.dump(json_obj, f, indent=4, ensure_ascii=False)


def download_file(url: str, filename: str, dirpath: str):
    os.makedirs(TMP_DIRPATH, exist_ok=True)

    tmp_filename = str(uuid4())
    proc = subprocess.run(
        [
            "aria2c",
            "-q",
            "-d",
            TMP_DIRPATH,
            "-o",
            tmp_filename,
            "--auto-file-renaming=false",
            url,
        ]
    )

    os.makedirs(dirpath, exist_ok=True)

    os.replace(os.path.join(TMP_DIRPATH, tmp_filename), os.path.join(dirpath, filename))


def is_valid_res_version(res_version: str) -> bool:
    return re.fullmatch("[0-9A-Fa-f-_]*", res_version) is not None


def is_valid_asset_filename(asset_filename: str) -> bool:
    return is_valid_filename(asset_filename)


def get_asset_filename(ab_filepath: str) -> str:
    asset_filename = (
        os.path.splitext(ab_filepath)[0].replace("/", "_").replace("#", "__") + ".dat"
    )

    return asset_filename


AK_BATTLE_LOG_KEY = "pM6Umv*^hVQuB6t&"


def decode_battle_log(player_data, raw_data):
    t = player_data["pushFlags"]["status"]
    key = md5(f"{AK_BATTLE_LOG_KEY}{t}".encode()).digest()

    battle_log = bytes.fromhex(raw_data)
    ciphertext = battle_log[:-16]
    iv = battle_log[-16:]

    cipher = AES.new(key, AES.MODE_CBC, iv)

    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

    decoded_battle_log = json.loads(plaintext)

    return decoded_battle_log


def convert_char_obj_to_tower_char_obj(char_obj: dict, tower_char_idx: int):
    char_obj["relation"] = str(char_obj["instId"])
    char_obj["instId"] = str(tower_char_idx)

    char_obj["type"] = "CHAR"


def sort_json_obj_lst(target_lst: list) -> None:
    target_lst.sort(key=lambda k: json.dumps(k))


def validate_is_cheat(is_cheat: str, battle_id: str):
    char_arr = []
    for i in battle_id:
        char_arr.append(chr(ord(i) + 7))
    dst_is_cheat = b64encode("".join(char_arr).encode()).decode()
    return is_cheat == dst_is_cheat


def get_random_key(key_probability_dict: dict):
    r = random.random()
    p = 0
    for key, probability in key_probability_dict.items():
        p += probability
        if r < p:
            return key
    return None


str_tag_dict = {
    "PIONEER": "Vanguard",
    "WARRIOR": "Guard",
    "TANK": "Defender",
    "SNIPER": "Sniper",
    "CASTER": "Caster",
    "MEDIC": "Medic",
    "SUPPORT": "Supporter",
    "SPECIAL": "Specialist",
    "MELEE": "Melee",
    "RANGED": "Ranged",
    "TIER_6": "Top Operator",
    "TIER_5": "Senior Operator",
}


def get_char_str_tag_lst(char_obj):
    char_str_tag_lst = []

    char_str_tag_lst.append(str_tag_dict[char_obj["profession"]])

    char_str_tag_lst.append(str_tag_dict[char_obj["position"]])

    if char_obj["rarity"] in str_tag_dict:
        char_str_tag_lst.append(str_tag_dict[char_obj["rarity"]])

    if char_obj["tagList"] is not None:
        char_str_tag_lst += char_obj["tagList"].copy()

    return char_str_tag_lst
