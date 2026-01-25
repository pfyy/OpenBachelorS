from copy import deepcopy
from functools import wraps
import os
import json
from enum import Enum
import inspect
import asyncio
import logging
import time

from psycopg.types.json import Json
from fastapi import Response
import orjson
from psycopg import sql

from ..const.json_const import true, false, null
from ..const.filepath import (
    CONFIG_JSON,
    VERSION_JSON,
    SQUAD_JSON,
    TMPL_JSON,
    RLV2_TMPL_JSON,
    SANDBOX_TMPL_JSON,
    CRISIS_V2_TMPL_JSON,
    MESSAGE_JSON,
    SKIN_TABLE,
    CHARWORD_TABLE,
    UNIEQUIP_TABLE,
    CHARACTER_TABLE,
    STORY_TABLE,
    STAGE_TABLE,
    HANDBOOK_INFO_TABLE,
    RETRO_TABLE,
    DISPLAY_META_TABLE,
    MEDAL_TABLE,
    STORY_REVIEW_TABLE,
    STORY_REVIEW_META_TABLE,
    ENEMY_HANDBOOK_TABLE,
    ACTIVITY_TABLE,
    CHAR_PATCH_TABLE,
    CLIMB_TOWER_TABLE,
    BUILDING_DATA,
    SAV_DELTA_JSON,
    SAV_PENDING_DELTA_JSON,
    MULTI_USER_SAV_DIRPATH,
    REPLAY_DIRPATH,
    MULTI_REPLAY_DIRPATH,
    EXTRA_SAVE_FILEPATH,
    MULTI_EXTRA_SAVE_DIRPATH,
    ROGUELIKE_TOPIC_TABLE,
    CAMPAIGN_TABLE,
)
from .const_json_loader import const_json_loader, ConstJson, ConstJsonLike, SavableThing
from .battle_replay_manager import BattleReplayManager, DBBattleReplayManager
from .extra_save import ExtraSave, DBExtraSave
from .helper import (
    is_char_id,
    get_char_num_id,
    load_delta_json_obj,
    save_delta_json_obj,
    get_username_by_token,
)
from .db_manager import IS_DB_READY, get_db_conn_or_pool, create_user_if_necessary
from .log_helper import IS_DEBUG

logger = logging.getLogger(__name__)


def build_player_data_template():
    tmpl_json_obj = const_json_loader[TMPL_JSON].copy()

    # ----------

    skin_table = const_json_loader[SKIN_TABLE]
    charword_table = const_json_loader[CHARWORD_TABLE]
    uniequip_table = const_json_loader[UNIEQUIP_TABLE]
    character_table = const_json_loader[CHARACTER_TABLE]
    char_patch_table = const_json_loader[CHAR_PATCH_TABLE]

    char_id_skin_id_dict = {}

    for skin_id, skin_obj in skin_table["charSkins"]:
        if "@" not in skin_id:
            continue

        tmpl_json_obj["skin"]["characterSkins"][skin_id] = 1
        tmpl_json_obj["skin"]["skinTs"][skin_id] = 1700000000

        char_id = skin_obj["charId"]

        tmpl_id = skin_obj["tmplId"]
        if tmpl_id is not None:
            char_id = tmpl_id

        if char_id not in char_id_skin_id_dict:
            char_id_skin_id_dict[char_id] = skin_id
        else:
            prev_skin_id = char_id_skin_id_dict[char_id]
            if (
                skin_table["charSkins"][skin_id]["displaySkin"]["getTime"]
                >= skin_table["charSkins"][prev_skin_id]["displaySkin"]["getTime"]
            ):
                char_id_skin_id_dict[char_id] = skin_id

    char_id_lst = []

    max_char_num_id = 0

    for char_id, char_obj in character_table:
        if not is_char_id(char_id):
            continue

        if char_id == "char_512_aprot":
            continue

        char_id_lst.append(char_id)

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
            "level": char_obj["phases"][-1]["maxLevel"],
            "exp": 0,
            "evolvePhase": len(char_obj["phases"]) - 1,
            "defaultSkillIndex": len(char_obj["skills"]) - 1,
            "gainTime": 1700000000,
            "skills": [],
            "voiceLan": voice_lan,
            "currentEquip": None,
            "equip": {},
            "starMark": 0,
        }

        for i, skill_obj in char_obj["skills"]:
            player_data_char_obj["skills"].append(
                {
                    "skillId": skill_obj["skillId"],
                    "unlock": 1,
                    "state": 0,
                    "specializeLevel": len(skill_obj["levelUpCostCond"]),
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

        # --- amiya ---
        if char_id in char_patch_table["infos"]:
            player_data_char_obj["currentTmpl"] = char_id
            player_data_char_obj["tmpl"] = {}

            player_data_char_obj["tmpl"][char_id] = {
                "skinId": player_data_char_obj["skin"],
                "defaultSkillIndex": player_data_char_obj["defaultSkillIndex"],
                "skills": player_data_char_obj["skills"],
                "currentEquip": player_data_char_obj["currentEquip"],
                "equip": player_data_char_obj["equip"],
            }

            player_data_char_obj["skin"] = null
            player_data_char_obj["defaultSkillIndex"] = -1
            player_data_char_obj["skills"] = []
            player_data_char_obj["currentEquip"] = null
            player_data_char_obj["equip"] = {}

            for i, tmpl_id in char_patch_table["infos"][char_id]["tmplIds"]:
                if tmpl_id == char_id:
                    continue

                if tmpl_id in char_id_skin_id_dict:
                    skin_id = char_id_skin_id_dict[tmpl_id]
                else:
                    skin_id = skin_table["buildinPatchMap"][char_id][tmpl_id]

                player_data_char_tmpl_obj = {
                    "skinId": skin_id,
                    "defaultSkillIndex": len(
                        char_patch_table["patchChars"][tmpl_id]["skills"]
                    )
                    - 1,
                    "skills": [],
                    "currentEquip": None,
                    "equip": {},
                }

                for i, skill_obj in char_patch_table["patchChars"][tmpl_id]["skills"]:
                    player_data_char_tmpl_obj["skills"].append(
                        {
                            "skillId": skill_obj["skillId"],
                            "unlock": 1,
                            "state": 0,
                            "specializeLevel": len(skill_obj["levelUpCostCond"]),
                            "completeUpgradeTime": -1,
                        },
                    )

                if tmpl_id in uniequip_table["charEquip"]:
                    for i, uniequip_id in uniequip_table["charEquip"][tmpl_id]:
                        if uniequip_id.startswith("uniequip_001_"):
                            uniequip_level = 1
                        else:
                            uniequip_level = 3
                        player_data_char_tmpl_obj["equip"][uniequip_id] = {
                            "hide": 0,
                            "locked": 0,
                            "level": uniequip_level,
                        }

                    player_data_char_tmpl_obj["currentEquip"] = uniequip_table[
                        "charEquip"
                    ][tmpl_id][-1]

                player_data_char_obj["tmpl"][tmpl_id] = player_data_char_tmpl_obj

        tmpl_json_obj["troop"]["chars"][str(char_num_id)] = player_data_char_obj

    tmpl_json_obj["troop"]["curCharInstId"] = max_char_num_id + 1

    char_id_lst = ConstJson(char_id_lst)

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

        if stage_id.startswith("camp_"):
            tmpl_json_obj["campaignsV2"]["open"]["permanent"].append(stage_id)
            tmpl_json_obj["campaignsV2"]["instances"][stage_id] = {
                "maxKills": 400,
                "rewardStatus": [1, 1, 1, 1, 1, 1, 1, 1],
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

    display_meta_table = const_json_loader[DISPLAY_META_TABLE]

    for i, avatar_obj in display_meta_table["playerAvatarData"]["avatarList"]:
        avatar_id = avatar_obj["avatarId"]
        tmpl_json_obj["avatar"]["avatar_icon"][avatar_id] = {
            "ts": 1700000000,
            "src": "initial",
        }

    for namecard_id, namecard_obj in display_meta_table["nameCardV2Data"]["skinData"]:
        tmpl_json_obj["nameCardStyle"]["skin"]["state"][namecard_id] = {
            "unlock": true,
            "progress": null,
        }

    for i, bg_obj in display_meta_table["homeBackgroundData"]["homeBgDataList"]:
        bg_id = bg_obj["bgId"]
        tmpl_json_obj["background"]["bgs"][bg_id] = {"unlock": 1700000000}

    for i, theme_obj in display_meta_table["homeBackgroundData"]["themeList"]:
        theme_id = theme_obj["id"]
        tmpl_json_obj["homeTheme"]["themes"][theme_id] = {"unlock": 1700000000}

    # ----------

    medal_table = const_json_loader[MEDAL_TABLE]
    for i, medal_obj in medal_table["medalList"]:
        medal_id = medal_obj["medalId"]
        tmpl_json_obj["medal"]["medals"][medal_id] = {
            "id": medal_id,
            "val": [],
            "fts": 1700000000,
            "rts": 1700000000,
        }

    # ----------

    story_review_table = const_json_loader[STORY_REVIEW_TABLE]
    story_review_meta_table = const_json_loader[STORY_REVIEW_META_TABLE]

    for story_review_id, story_review_obj in story_review_table:
        tmpl_json_obj["storyreview"]["groups"][story_review_id] = {
            "rts": 1700000000,
            "stories": [],
            "trailRewards": [],
        }
        for i, story_obj in story_review_table[story_review_id]["infoUnlockDatas"]:
            story_id = story_obj["storyId"]
            tmpl_json_obj["storyreview"]["groups"][story_review_id]["stories"].append(
                {"id": story_id, "uts": 1700000000, "rc": 1}
            )
        if (
            story_review_id
            in story_review_meta_table["miniActTrialData"]["miniActTrialDataMap"]
        ):
            for i, reward_obj in story_review_meta_table["miniActTrialData"][
                "miniActTrialDataMap"
            ][story_review_id]["rewardList"]:
                reward_id = reward_obj["trialRewardId"]
                tmpl_json_obj["storyreview"]["groups"][story_review_id][
                    "trailRewards"
                ].append(reward_id)

    # ----------

    enemy_handbook_table = const_json_loader[ENEMY_HANDBOOK_TABLE]
    for enemy_id, enemy_obj in enemy_handbook_table["enemyData"]:
        tmpl_json_obj["dexNav"]["enemy"]["enemies"][enemy_id] = 1

    # ----------

    activity_table = const_json_loader[ACTIVITY_TABLE]
    for activity_type_id, activity_type_obj in activity_table["activity"]:
        if activity_type_id not in tmpl_json_obj["activity"]:
            tmpl_json_obj["activity"][activity_type_id] = {}
        for activity_id, activity_obj in activity_table["activity"][activity_type_id]:
            if activity_id not in tmpl_json_obj["activity"][activity_type_id]:
                tmpl_json_obj["activity"][activity_type_id][activity_id] = {}

    # ----------

    april_fool_activity_id = "act5fun"

    for activity_id, activity_obj in activity_table["basicInfo"]:
        if activity_obj["type"] == "APRIL_FOOL":
            if (
                activity_obj["startTime"]
                > activity_table["basicInfo"][april_fool_activity_id]["startTime"]
            ):
                april_fool_activity_id = activity_id

    if "APRIL_FOOL" not in tmpl_json_obj["activity"]:
        tmpl_json_obj["activity"]["APRIL_FOOL"] = {}
    tmpl_json_obj["activity"]["APRIL_FOOL"][april_fool_activity_id] = {"isOpen": true}

    # ----------

    climb_tower_table = const_json_loader[CLIMB_TOWER_TABLE]

    tower_id_lst = []

    for tower_id, tower_obj in climb_tower_table["towers"]:
        if tower_obj["towerType"] == "TRAINING":
            continue

        tower_id_lst.append(tower_id)

        tmpl_json_obj["tower"]["outer"]["towers"][tower_id] = {
            "best": 6,
            "reward": [1, 2, 3, 4, 5, 6],
            "unlockHard": true,
            "hardBest": 6,
            "canSweep": true,
            "canSweepHard": true,
        }

    tower_id_lst = ConstJson(tower_id_lst)

    for card_id, card_obj in climb_tower_table["mainCards"]:
        tmpl_json_obj["tower"]["outer"]["pickedGodCard"][card_id] = card_obj[
            "subCardIds"
        ].copy()

        tmpl_json_obj["tower"]["season"]["passWithGodCard"][card_id] = (
            tower_id_lst.copy()
        )

    tower_season = const_json_loader[VERSION_JSON]["tower_season"]
    if not tower_season:
        tower_season_num_id = 1
        while True:
            cur_tower_season = f"tower_season_{tower_season_num_id}"
            if cur_tower_season in climb_tower_table["seasonInfos"]:
                tower_season = cur_tower_season
                tower_season_num_id += 1
            else:
                break
    tmpl_json_obj["tower"]["season"]["id"] = tower_season

    for mission_id, mission_obj in climb_tower_table["missionData"]:
        tmpl_json_obj["tower"]["season"]["missions"][mission_id] = {
            "value": 1,
            "target": 1,
            "hasRecv": true,
        }

    # ----------

    for i, char_id in char_id_lst:
        if character_table[char_id]["isNotObtainable"]:
            continue
        char_num_id = get_char_num_id(char_id)
        tmpl_json_obj["building"]["chars"][str(char_num_id)] = {
            "charId": char_id,
            "lastApAddTime": 1700000000,
            "ap": 8640000,
            "roomSlotId": "",
            "index": -1,
            "changeScale": 0,
            "bubble": {
                "normal": {"add": -1, "ts": 0},
                "assist": {"add": -1, "ts": 0},
                "private": {"add": -1, "ts": 0},
            },
            "workTime": 0,
            "privateRooms": [],
        }

    # place amiya in MEETING by default to avoid error msg
    tmpl_json_obj["building"]["roomSlots"]["slot_36"]["charInstIds"] = [2, -1]
    tmpl_json_obj["building"]["chars"]["2"]["roomSlotId"] = "slot_36"
    tmpl_json_obj["building"]["chars"]["2"]["index"] = 0

    building_data = const_json_loader[BUILDING_DATA]

    for furniture_id, furniture_obj in building_data["customData"]["furnitures"]:
        tmpl_json_obj["building"]["furniture"][furniture_id] = {
            "count": 9999,
            "inUse": 0,
        }

    for music_id, music_obj in building_data["musicData"]["musicDatas"]:
        tmpl_json_obj["building"]["music"]["state"][music_id] = {
            "progress": null,
            "unlock": true,
        }

    # ----------

    rlv2_tmpl_json_obj = const_json_loader[RLV2_TMPL_JSON].copy()

    roguelike_topic_table = const_json_loader[ROGUELIKE_TOPIC_TABLE]

    for theme_id, theme_obj in roguelike_topic_table["topics"]:
        if theme_id not in rlv2_tmpl_json_obj["outer"]:
            rlv2_tmpl_json_obj["outer"][theme_id] = {
                "collect": {
                    "mode": {
                        "NORMAL": {"state": 1, "progress": null},
                        "MONTH_TEAM": {"state": 1, "progress": null},
                        "CHALLENGE": {"state": 1, "progress": null},
                    },
                    "modeGrade": {
                        "NORMAL": {
                            "0": {"state": 2, "progress": null},
                            "1": {"state": 2, "progress": null},
                            "2": {"state": 2, "progress": null},
                            "3": {"state": 2, "progress": null},
                            "4": {"state": 2, "progress": null},
                            "5": {"state": 2, "progress": null},
                            "6": {"state": 2, "progress": null},
                            "7": {"state": 2, "progress": null},
                            "8": {"state": 2, "progress": null},
                            "9": {"state": 2, "progress": null},
                            "10": {"state": 2, "progress": null},
                            "11": {"state": 2, "progress": null},
                            "12": {"state": 2, "progress": null},
                            "13": {"state": 2, "progress": null},
                            "14": {"state": 2, "progress": null},
                            "15": {"state": 2, "progress": null},
                            "16": {"state": 2, "progress": null},
                            "17": {"state": 2, "progress": null},
                            "18": {"state": 2, "progress": null},
                        },
                        "MONTH_TEAM": {"0": {"state": 2, "progress": null}},
                        "CHALLENGE": {"0": {"state": 2, "progress": null}},
                    },
                },
                "record": {
                    "stageCnt": {},
                    "bandGrade": {},
                },
            }

            for stage_id, stage_obj in roguelike_topic_table["details"][theme_id][
                "stages"
            ]:
                rlv2_tmpl_json_obj["outer"][theme_id]["record"]["stageCnt"][
                    stage_id
                ] = 1

    tmpl_json_obj["rlv2"] = rlv2_tmpl_json_obj

    # ----------

    sandbox_tmpl_json_obj = const_json_loader[SANDBOX_TMPL_JSON].copy()

    tmpl_json_obj["sandboxPerm"] = sandbox_tmpl_json_obj

    # ----------

    crisis_v2_tmpl_json_obj = const_json_loader[CRISIS_V2_TMPL_JSON].copy()

    crisis_v2_season = const_json_loader[VERSION_JSON]["crisis_v2_season"]

    if not crisis_v2_season:
        crisis_v2_season = ""

    crisis_v2_tmpl_json_obj["current"] = crisis_v2_season

    tmpl_json_obj["crisisV2"] = crisis_v2_tmpl_json_obj

    # ----------

    squad_json = const_json_loader[SQUAD_JSON]

    default_squad = []

    for i, squad_char_obj in squad_json["default"]:
        default_squad.append(
            {
                "charInstId": get_char_num_id(squad_char_obj["char_id"]),
                "skillIndex": squad_char_obj["skill_index"],
                "currentEquip": squad_char_obj["current_equip"],
            }
        )

    for i in range(len(default_squad), 12):
        default_squad.append(null)

    for i in range(4):
        tmpl_json_obj["troop"]["squads"][str(i)]["slots"] = default_squad

    # ----------

    for slot_obj in tmpl_json_obj["recruit"]["normal"]["slots"].values():
        slot_obj["tags"] = [11, 2, 10, 19, 14]

    # ----------

    # temporary

    if str(get_char_num_id("char_4195_radian")) in tmpl_json_obj["troop"]["chars"]:
        tmpl_json_obj["troop"]["chars"][str(get_char_num_id("char_4195_radian"))][
            "master"
        ] = {
            "master_radian_1": 2,
            "master_radian_2": 1,
            "master_radian_3": 3,
            "master_radian_4": 3,
            "master_radian_5": 3,
            "master_radian_6": 3,
        }

    # ----------

    campaign_table = const_json_loader[CAMPAIGN_TABLE]

    tmpl_json_obj["campaignsV2"]["open"]["rGroup"] = campaign_table[
        "campaignRotateStageOpenTimes"
    ][-1]["groupId"]

    # ----------

    player_data_template = ConstJson(tmpl_json_obj)
    return player_data_template, char_id_lst


player_data_template, char_id_lst = build_player_data_template()


class DeltaJsonBaseState(Enum):
    DEFAULT = 0
    DELETED = 1


class DeltaJsonOverlayState(Enum):
    MISSING = 0
    DICT = 1
    NON_DICT = 2


class _DeltaJsonDeleteOp:
    pass


DeltaJsonDeleteOp = _DeltaJsonDeleteOp()


class DeltaJson:
    def __init__(
        self,
        modified_dict=None,
        deleted_dict=None,
    ):
        if modified_dict is None:
            self.modified_dict = {}
        else:
            self.modified_dict = modified_dict
        if deleted_dict is None:
            self.deleted_dict = {}
        else:
            self.deleted_dict = deleted_dict

    def reset(self):
        self.modified_dict = {}
        self.deleted_dict = {}

    def reset_key(self, key):
        if key in self.modified_dict:
            del self.modified_dict[key]

        if key in self.deleted_dict:
            del self.deleted_dict[key]

    def get_child_delta_json(self, key):
        if key not in self.modified_dict:
            self.modified_dict[key] = {}

        if key not in self.deleted_dict:
            self.deleted_dict[key] = {}

        return DeltaJson(self.modified_dict[key], self.deleted_dict[key])

    def get_key_status(self, key):
        if key in self.deleted_dict and self.deleted_dict[key] is None:
            base_state = DeltaJsonBaseState.DELETED
        else:
            base_state = DeltaJsonBaseState.DEFAULT

        if key in self.modified_dict:
            if isinstance(self.modified_dict[key], dict):
                overlay_state = DeltaJsonOverlayState.DICT
            else:
                overlay_state = DeltaJsonOverlayState.NON_DICT
        else:
            overlay_state = DeltaJsonOverlayState.MISSING

        return base_state, overlay_state

    def get_key_value(self, key):
        return self.modified_dict[key]

    def set_key_primitive_value(self, key, primitive_value, is_in_base):
        if isinstance(primitive_value, dict) and primitive_value:
            raise ValueError(
                f"DeltaJson: internal err, non empty dict primitive_value {primitive_value}"
            )

        if primitive_value == DeltaJsonDeleteOp:
            self.modified_dict.pop(key, None)
        else:
            self.modified_dict[key] = primitive_value

        if is_in_base:
            self.deleted_dict[key] = None


EmptyConstJson = ConstJson({})


def recursive_delete(base_dict: dict, deleted_dict: dict):
    for key, value in deleted_dict.items():
        if isinstance(value, dict):
            recursive_delete(base_dict[key], value)
        else:
            del base_dict[key]


def recursive_update(base_dict: dict, overlay_dict: dict):
    for key, value in overlay_dict.items():
        if (
            key in base_dict
            and isinstance(base_dict[key], dict)
            and isinstance(value, dict)
        ):
            recursive_update(base_dict[key], value)
        else:
            base_dict[key] = value


class OverlayJson(ConstJsonLike):
    def __init__(self, const_json_like: ConstJsonLike, delta_json: DeltaJson):
        self.const_json_like = const_json_like
        self.delta_json = delta_json

    def _contains(self, key, base_state, overlay_state):
        if base_state == DeltaJsonBaseState.DEFAULT:
            return key in self.const_json_like or key in self.delta_json.modified_dict
        else:
            if overlay_state == DeltaJsonOverlayState.MISSING:
                return False
            return True

    def __contains__(self, key):
        base_state, overlay_state = self.delta_json.get_key_status(key)

        return self._contains(key, base_state, overlay_state)

    def __getitem__(self, key):
        base_state, overlay_state = self.delta_json.get_key_status(key)

        if not self._contains(key, base_state, overlay_state):
            raise KeyError(f"OverlayJson: key {key} not found")

        if base_state == DeltaJsonBaseState.DEFAULT and key in self.const_json_like:
            value = self.const_json_like[key]
            if (isinstance(value, ConstJson) and value.is_dict) or isinstance(
                value, OverlayJson
            ):
                return OverlayJson(value, self.delta_json.get_child_delta_json(key))
            return value

        value = self.delta_json.get_key_value(key)

        if isinstance(value, dict):
            return OverlayJson(
                EmptyConstJson, self.delta_json.get_child_delta_json(key)
            )
        else:
            if isinstance(value, list):
                return ConstJson(value)
            return value

    def __iter__(self):
        done_key_set = set()
        for key, value in self.const_json_like:
            if key in self and key not in done_key_set:
                done_key_set.add(key)
                yield key, self[key]

        for key in self.delta_json.modified_dict:
            if key in self and key not in done_key_set:
                done_key_set.add(key)
                yield key, self[key]

    def __len__(self):
        i = 0
        for key, value in self:
            i += 1
        return i

    def copy(self):
        json_obj = self.const_json_like.copy()

        recursive_delete(json_obj, self.delta_json.deleted_dict)

        modified_dict = deepcopy(self.delta_json.modified_dict)
        recursive_update(json_obj, modified_dict)
        return json_obj

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            if key not in self or not isinstance(self[key], OverlayJson):
                self.delta_json.set_key_primitive_value(
                    key, {}, key in self.const_json_like
                )
            child_overlay_json = self[key]
            for k, v in value.items():
                child_overlay_json[k] = v
        else:
            self.delta_json.set_key_primitive_value(
                key, value, key in self.const_json_like
            )

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(f"OverlayJson: key {key} not found")
        self.delta_json.set_key_primitive_value(
            key, DeltaJsonDeleteOp, key in self.const_json_like
        )


def recursive_flush_deleted_dict(
    overlay_json: OverlayJson,
    delta_json: DeltaJson,
    parent_hg_deleted_dict: dict,
    parent_key: str,
):
    deleted_key_lst = []
    internal_deleted_key_lst = []
    for key, value in delta_json.deleted_dict.items():
        if not isinstance(value, dict):
            if key not in delta_json.modified_dict:
                deleted_key_lst.append(key)
                del overlay_json[key]
            else:
                internal_deleted_key_lst.append(key)

    for key in internal_deleted_key_lst:
        del delta_json.deleted_dict[key]

    if deleted_key_lst:
        parent_hg_deleted_dict[parent_key] = deleted_key_lst

        for key in deleted_key_lst:
            del delta_json.deleted_dict[key]
    else:
        parent_hg_deleted_dict[parent_key] = {}

        for key, value in delta_json.deleted_dict.items():
            if key in overlay_json:
                child_overlay_json = overlay_json[key]
                child_delta_json = delta_json.get_child_delta_json(key)
                recursive_flush_deleted_dict(
                    child_overlay_json,
                    child_delta_json,
                    parent_hg_deleted_dict[parent_key],
                    key,
                )


def recursive_collapse_deleted_dict(target_dict: dict):
    deleted_key_lst = []

    for key in target_dict:
        value = target_dict[key]
        if isinstance(value, dict):
            if value:
                recursive_collapse_deleted_dict(value)
            value = target_dict[key]

            if not value:
                deleted_key_lst.append(key)

    for key in deleted_key_lst:
        del target_dict[key]


class FileBasedDeltaJson(DeltaJson, SavableThing):
    @classmethod
    async def create(cls, path: str):
        json_obj = await load_delta_json_obj(path)

        delta_json = cls(
            modified_dict=json_obj["modified"], deleted_dict=json_obj["deleted"]
        )

        delta_json.path = path

        return delta_json

    async def save(self):
        await save_delta_json_obj(self.path, self.modified_dict, self.deleted_dict)


class DBBasedDeltaJson(DeltaJson, SavableThing):
    @classmethod
    async def create(
        cls,
        column_name: str,
        username: str,
        save_aggregator=None,
    ):
        if save_aggregator is None:
            json_obj = await cls.load_delta_json_obj_from_db(column_name, username)
        else:
            json_obj = save_aggregator.get(column_name)
        if not json_obj:
            json_obj = {"modified": {}, "deleted": {}}

        delta_json = cls(
            modified_dict=json_obj["modified"], deleted_dict=json_obj["deleted"]
        )

        delta_json.column_name = column_name
        delta_json.username = username
        delta_json.save_aggregator = save_aggregator

        return delta_json

    @classmethod
    async def load_delta_json_obj_from_db(cls, column_name: str, username: str):
        pool = get_db_conn_or_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    sql.SQL(
                        "SELECT {column_name} FROM player_data WHERE username = %s",
                    ).format(column_name=sql.Identifier(column_name)),
                    (username,),
                )
                return (await cur.fetchone())[0]

    async def save(self):
        save_obj = Json(
            {
                "modified": self.modified_dict,
                "deleted": self.deleted_dict,
            }
        )
        if self.save_aggregator is not None:
            self.save_aggregator.set(
                self.column_name,
                save_obj,
            )
            return
        pool = get_db_conn_or_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    sql.SQL(
                        "UPDATE player_data SET {column_name} = %s WHERE username = %s",
                    ).format(column_name=sql.Identifier(self.column_name)),
                    (
                        save_obj,
                        self.username,
                    ),
                )
                await conn.commit()


class DBSaveAggregator:
    def __init__(self, username):
        self.username = username
        self.kv_dict = {}

    def get(self, key):
        return self.kv_dict.pop(key)

    def set(self, key, value):
        self.kv_dict[key] = value

    async def load(self):
        pool = get_db_conn_or_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT delta, pending_delta, extra FROM player_data WHERE username = %s",
                    (self.username,),
                )
                delta, pending_delta, extra = await cur.fetchone()

                self.set("delta", delta)
                self.set("pending_delta", pending_delta)
                self.set("extra", extra)

    async def save(self):
        pool = get_db_conn_or_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE player_data SET delta = %s, pending_delta = %s, extra = %s WHERE username = %s",
                    (
                        self.get("delta"),
                        self.get("pending_delta"),
                        self.get("extra"),
                        self.username,
                    ),
                )
                await conn.commit()


class PlayerData(OverlayJson, SavableThing):
    DEFAULT_TOKEN = "_"

    @classmethod
    async def create(cls, player_id=None, request=None):
        if request is not None:
            token = request.headers.get("secret", cls.DEFAULT_TOKEN)
        else:
            if player_id is not None:
                token = player_id
            else:
                token = cls.DEFAULT_TOKEN

        username = get_username_by_token(token)

        config = const_json_loader[CONFIG_JSON]
        if config["multi_user"]:
            if IS_DB_READY:
                await create_user_if_necessary(username)

                save_aggregator = DBSaveAggregator(username)

                await save_aggregator.load()

                (
                    sav_delta_json,
                    sav_pending_delta_json,
                    extra_save,
                ) = await asyncio.gather(
                    DBBasedDeltaJson.create(
                        "delta",
                        username,
                        save_aggregator,
                    ),
                    DBBasedDeltaJson.create(
                        "pending_delta",
                        username,
                        save_aggregator,
                    ),
                    DBExtraSave.create(
                        username,
                        save_aggregator,
                    ),
                )

                battle_replay_manager = DBBattleReplayManager(
                    username,
                )
            else:
                save_aggregator = None

                (
                    sav_delta_json,
                    sav_pending_delta_json,
                    extra_save,
                ) = await asyncio.gather(
                    FileBasedDeltaJson.create(
                        os.path.join(MULTI_USER_SAV_DIRPATH, username, "delta.json")
                    ),
                    FileBasedDeltaJson.create(
                        os.path.join(
                            MULTI_USER_SAV_DIRPATH, username, "pending_delta.json"
                        )
                    ),
                    ExtraSave.create(
                        os.path.join(MULTI_EXTRA_SAVE_DIRPATH, username, "extra.json")
                    ),
                )

                battle_replay_manager = BattleReplayManager(
                    os.path.join(MULTI_REPLAY_DIRPATH, username)
                )
        else:
            save_aggregator = None

            (
                sav_delta_json,
                sav_pending_delta_json,
                extra_save,
            ) = await asyncio.gather(
                FileBasedDeltaJson.create(SAV_DELTA_JSON),
                FileBasedDeltaJson.create(SAV_PENDING_DELTA_JSON),
                ExtraSave.create(EXTRA_SAVE_FILEPATH),
            )

            battle_replay_manager = BattleReplayManager(REPLAY_DIRPATH)

        json_with_delta = OverlayJson(player_data_template, sav_delta_json)
        player_data = cls(json_with_delta, sav_pending_delta_json)

        player_data.save_aggregator = save_aggregator
        player_data.sav_delta_json = sav_delta_json
        player_data.sav_pending_delta_json = sav_pending_delta_json
        player_data.battle_replay_manager = battle_replay_manager
        player_data.extra_save = extra_save
        player_data.json_with_delta = json_with_delta

        return player_data

    async def save(self):
        await asyncio.gather(
            self.sav_delta_json.save(),
            self.sav_pending_delta_json.save(),
            self.extra_save.save(),
        )

        if self.save_aggregator is not None:
            await self.save_aggregator.save()

    def reset(self):
        self.sav_delta_json.reset()
        self.sav_pending_delta_json.reset()
        self.extra_save.reset()

    def reset_key(self, key):
        self.sav_delta_json.reset_key(key)
        self.sav_pending_delta_json.reset_key(key)

    def build_delta_response(self):
        helper_dict = {}
        helper_str = "_"
        recursive_flush_deleted_dict(
            self.json_with_delta, self.sav_pending_delta_json, helper_dict, helper_str
        )
        hg_deleted_dict = helper_dict[helper_str]

        hg_modifed_dict = deepcopy(self.sav_pending_delta_json.modified_dict)
        for key, value in self.sav_pending_delta_json.modified_dict.items():
            self.json_with_delta[key] = value
        self.sav_pending_delta_json.modified_dict = {}

        recursive_collapse_deleted_dict(self.sav_delta_json.deleted_dict)
        recursive_collapse_deleted_dict(self.sav_pending_delta_json.deleted_dict)

        recursive_collapse_deleted_dict(hg_deleted_dict)

        return {"modified": hg_modifed_dict, "deleted": hg_deleted_dict}


MESSAGE_COOLDOWN = 60


def handle_message(player_data, json_response):
    cur_ts = time.time()
    last_message_ts = player_data.extra_save.save_obj.get("last_message_ts", 0)

    if cur_ts - last_message_ts < MESSAGE_COOLDOWN:
        return

    message_json = const_json_loader[MESSAGE_JSON]

    received_message_lst = player_data.extra_save.save_obj["received_message_lst"]

    for message_idx, message_obj in message_json["message_lst"]:
        message_id = message_obj["message_id"]
        if message_id not in received_message_lst:
            received_message_lst.append(message_id)

            message_str = message_obj["message_str"]
            payload_obj = {
                "content": message_str,
                "loop": 3,
                "majorVersion": "369",
            }

            json_response["pushMessage"] = [
                {
                    "path": "flushAlerts",
                    "payload": {"data": json.dumps(payload_obj)},
                }
            ]

            player_data.extra_save.save_obj["last_message_ts"] = cur_ts

            break


def player_data_decorator(func):
    func_sig = inspect.signature(func)
    func_param_lst = [
        i for i in func_sig.parameters.values() if i.name != "player_data"
    ]

    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        player_data = await PlayerData.create(request=request)
        json_response = await func(player_data, *args, **kwargs)

        if not isinstance(json_response, dict):
            return json_response

        handle_message(player_data, json_response)

        delta_response = player_data.build_delta_response()
        await player_data.save()

        json_response["playerDataDelta"] = delta_response

        if IS_DEBUG:
            delta_response_str = json.dumps(delta_response, ensure_ascii=False)
            logger.debug(delta_response_str)

        return Response(
            content=orjson.dumps(json_response), media_type="application/json"
        )

    wrapper.__signature__ = func_sig.replace(parameters=func_param_lst)

    return wrapper
