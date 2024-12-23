from ..const.json_const import true, false, null
from ..const.filepath import (
    TMPL_JSON,
    SKIN_TABLE,
    CHARWORD_TABLE,
    UNIEQUIP_TABLE,
    CHARACTER_TABLE,
    STORY_TABLE,
    STAGE_TABLE,
    HANDBOOK_INFO_TABLE,
    RETRO_TABLE,
)
from .const_json_loader import const_json_loader, ConstJson
from .helper import is_char_id, get_char_num_id


def build_player_data_template():
    tmpl_json_obj = const_json_loader[TMPL_JSON].copy()

    # ----------

    skin_table = const_json_loader[SKIN_TABLE]
    charword_table = const_json_loader[CHARWORD_TABLE]
    uniequip_table = const_json_loader[UNIEQUIP_TABLE]
    character_table = const_json_loader[CHARACTER_TABLE]

    char_id_skin_id_dict = {}

    for skin_id, skin_obj in skin_table["charSkins"]:
        if "@" not in skin_id:
            continue

        tmpl_json_obj["skin"]["characterSkins"][skin_id] = 1
        tmpl_json_obj["skin"]["skinTs"][skin_id] = 1700000000

        char_id = skin_obj["charId"]
        if char_id not in char_id_skin_id_dict:
            char_id_skin_id_dict[char_id] = skin_id
        else:
            prev_skin_id = char_id_skin_id_dict[char_id]
            if (
                skin_table["charSkins"][skin_id]["displaySkin"]["getTime"]
                >= skin_table["charSkins"][prev_skin_id]["displaySkin"]["getTime"]
            ):
                char_id_skin_id_dict[char_id] = skin_id

    max_char_num_id = 0

    for char_id, char_obj in character_table:
        if not is_char_id(char_id):
            continue

        if char_id == "char_512_aprot":
            continue

        char_num_id = get_char_num_id(char_id)

        max_char_num_id = max(max_char_num_id, char_num_id)

        tmpl_json_obj["dexNav"]["character"][char_id] = {
            "charInstId": char_num_id,
            "count": 6,
            "classicCount": 0,
        }

        tmpl_json_obj["troop"]["charGroup"][char_id] = {"favorPoint": 25570}

        if char_id in char_id_skin_id_dict:
            skin_id = char_id_skin_id_dict[char_id]
        else:
            skin_id = None
            if char_id in skin_table["buildinEvolveMap"]:
                for i in range(2, -1, -1):
                    i = str(i)
                    if i in skin_table["buildinEvolveMap"][char_id]:
                        skin_id = skin_table["buildinEvolveMap"][char_id][i]
                        break

        if char_id in charword_table["charDefaultTypeDict"]:
            voice_lan = charword_table["charDefaultTypeDict"][char_id]
        else:
            voice_lan = "NONE"

        player_data_char_obj = {
            "instId": char_num_id,
            "charId": char_id,
            "favorPoint": 25570,
            "potentialRank": 5,
            "mainSkillLvl": 7,
            "skin": skin_id,
            "level": character_table[char_id]["phases"][-1]["maxLevel"],
            "exp": 0,
            "evolvePhase": len(character_table[char_id]["phases"]) - 1,
            "defaultSkillIndex": len(character_table[char_id]["skills"]) - 1,
            "gainTime": 1700000000,
            "skills": [],
            "voiceLan": voice_lan,
            "currentEquip": None,
            "equip": {},
            "starMark": 0,
        }

        for i, skill_obj in character_table[char_id]["skills"]:
            player_data_char_obj["skills"].append(
                {
                    "skillId": skill_obj["skillId"],
                    "unlock": 1,
                    "state": 0,
                    "specializeLevel": 3,
                    "completeUpgradeTime": -1,
                },
            )

        if char_id in uniequip_table["charEquip"]:
            for i, uniequip_id in uniequip_table["charEquip"][char_id]:
                if uniequip_id.startswith("uniequip_001_"):
                    uniequip_level = 1
                else:
                    uniequip_level = 3
                player_data_char_obj["equip"][uniequip_id] = {
                    "hide": 0,
                    "locked": 0,
                    "level": uniequip_level,
                }

            player_data_char_obj["currentEquip"] = uniequip_table["charEquip"][char_id][
                -1
            ]

        tmpl_json_obj["troop"]["chars"][str(char_num_id)] = player_data_char_obj

    tmpl_json_obj["troop"]["curCharInstId"] = max_char_num_id + 1

    # ----------

    story_table = const_json_loader[STORY_TABLE]
    for story_id, story_obj in story_table:
        tmpl_json_obj["status"]["flags"][story_id] = 1

    # ----------

    stage_table = const_json_loader[STAGE_TABLE]
    for stage_id, stage_obj in stage_table["stages"]:
        tmpl_json_obj["dungeon"]["stages"][stage_id] = {
            "stageId": stage_id,
            "completeTimes": 1,
            "startTimes": 1,
            "practiceTimes": 0,
            "state": 3,
            "hasBattleReplay": 0,
            "noCostCnt": 0,
        }

    # ----------

    handbook_info_table = const_json_loader[HANDBOOK_INFO_TABLE]

    for char_id, handbook_obj in handbook_info_table["handbookDict"]:
        if char_id not in tmpl_json_obj["troop"]["addon"]:
            tmpl_json_obj["troop"]["addon"][char_id] = {}
        tmpl_json_obj["troop"]["addon"][char_id]["story"] = {}
        for i, story_set_obj in handbook_info_table["handbookDict"][char_id][
            "handbookAvgList"
        ]:
            story_set_id = story_set_obj["storySetId"]
            tmpl_json_obj["troop"]["addon"][char_id]["story"][story_set_id] = {
                "fts": 1700000000,
                "rts": 1700000000,
            }

    for char_id, handbook_stage_obj in handbook_info_table["handbookStageData"]:
        if char_id not in tmpl_json_obj["troop"]["addon"]:
            tmpl_json_obj["troop"]["addon"][char_id] = {}
        stage_id = handbook_stage_obj["stageId"]
        tmpl_json_obj["troop"]["addon"][char_id]["stage"] = {
            stage_id: {
                "startTimes": 1,
                "completeTimes": 1,
                "state": 3,
                "fts": 1700000000,
                "rts": 1700000000,
            }
        }

    # ----------

    retro_table = const_json_loader[RETRO_TABLE]

    for block_id, block_obj in retro_table["retroActList"]:
        tmpl_json_obj["retro"]["block"][block_id] = {"locked": 0, "open": 1}

    for trail_id, trail_obj in retro_table["retroTrailList"]:
        tmpl_json_obj["retro"]["trail"][trail_id] = {}
        for i, reward_obj in trail_obj["trailRewardList"]:
            reward_id = reward_obj["trailRewardId"]
            tmpl_json_obj["retro"]["trail"][trail_id][reward_id] = 1

    # ----------

    player_data_template = ConstJson(tmpl_json_obj)
    return player_data_template


player_data_template = build_player_data_template()
