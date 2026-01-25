from .const_json_loader import ConstJson, const_json_loader
from ..const.filepath import CHARACTER_TABLE
from .player_data import char_id_lst

profession_lst = ConstJson(
    [
        "PIONEER",
        "WARRIOR",
        "TANK",
        "SNIPER",
        "CASTER",
        "MEDIC",
        "SUPPORT",
        "SPECIAL",
    ]
)


def build_profession_assist_lst_dict():
    profession_char_id_lst_dict = {}

    for i, profession in profession_lst:
        profession_char_id_lst_dict[profession] = []

    character_table = const_json_loader[CHARACTER_TABLE]

    for i, char_id in char_id_lst:
        if character_table[char_id]["rarity"] != "TIER_6":
            continue

        profession = character_table[char_id]["profession"]

        profession_char_id_lst_dict[profession].append(char_id)

    return ConstJson(profession_char_id_lst_dict)


profession_assist_lst_dict = build_profession_assist_lst_dict()
