from copy import deepcopy
from functools import wraps
import os
import json

import flask
from flask import request
from psycopg.types.json import Json

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
)
from .const_json_loader import const_json_loader, ConstJson
from .battle_replay_manager import BattleReplayManager, DBBattleReplayManager
from .extra_save import ExtraSave, DBExtraSave
from .helper import (
    is_char_id,
    get_char_num_id,
    load_delta_json_obj,
    save_delta_json_obj,
    get_username_by_token,
)
from .db_manager import IS_DB_READY, get_db_conn, create_user_if_necessary


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

    april_fool_activity_id = "act6fun"

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

    player_data_template = ConstJson(tmpl_json_obj)
    return player_data_template, char_id_lst


player_data_template, char_id_lst = build_player_data_template()


# always a dict-like object (unless no_dict is true)
class DeltaJson:
    def __init__(
        self,
        modified_dict=None,
        deleted_dict=None,
        is_root=True,
        parent=None,
        prev_key=None,
        no_dict=False,
        no_dict_val=None,
    ):
        self.is_root = is_root
        if is_root:
            if modified_dict is None:
                self.modified_dict = {}
            else:
                self.modified_dict = modified_dict
            if deleted_dict is None:
                self.deleted_dict = {}
            else:
                self.deleted_dict = deleted_dict
        else:
            self.modified_dict = modified_dict
            self.deleted_dict = deleted_dict
        self.parent = parent
        self.prev_key = prev_key
        self.no_dict = no_dict
        self.no_dict_val = no_dict_val

    def contains(self, key):
        if self.modified_dict is not None and key in self.modified_dict:
            return 1
        if (
            self.deleted_dict is not None
            and key in self.deleted_dict
            and self.deleted_dict[key] is None
        ):
            return -1
        return 0

    def __contains__(self, key):
        return self.contains(key) == 1

    def initialize_modified_dict_if_necessary(self):
        if self.modified_dict is None:
            self.parent.initialize_modified_dict_if_necessary()
            if self.modified_dict is None:
                self.modified_dict = {}
                self.parent.modified_dict[self.prev_key] = self.modified_dict

    def initialize_deleted_dict_if_necessary(self):
        if self.deleted_dict is None:
            self.parent.initialize_deleted_dict_if_necessary()
            if self.deleted_dict is None:
                self.deleted_dict = {}
                self.parent.deleted_dict[self.prev_key] = self.deleted_dict

    # def deinitialize_modified_dict_if_necessary(self):
    #     if not self.is_root and self.modified_dict == {}:
    #         self.modified_dict = None
    #         del self.parent.modified_dict[self.prev_key]
    #         self.parent.deinitialize_modified_dict_if_necessary()

    def deinitialize_deleted_dict_if_necessary(self):
        if not self.is_root and self.deleted_dict == {}:
            self.deleted_dict = None
            del self.parent.deleted_dict[self.prev_key]
            self.parent.deinitialize_deleted_dict_if_necessary()

    def __getitem__(self, key):
        if self.modified_dict is not None and key in self.modified_dict:
            if isinstance(self.modified_dict[key], dict):
                child_modified_dict = self.modified_dict[key]
                child_no_dict = False
                child_no_dict_val = None
            else:
                child_modified_dict = None
                child_no_dict = True
                child_no_dict_val = self.modified_dict[key]
        else:
            child_modified_dict = None
            child_no_dict = False
            child_no_dict_val = None

        if self.deleted_dict is not None and key in self.deleted_dict:
            child_deleted_dict = self.deleted_dict[key]
        else:
            child_deleted_dict = None

        return DeltaJson(
            modified_dict=child_modified_dict,
            deleted_dict=child_deleted_dict,
            is_root=False,
            parent=self,
            prev_key=key,
            no_dict=child_no_dict,
            no_dict_val=child_no_dict_val,
        )

    def __setitem__(self, key, value):
        value = deepcopy(value)
        self.initialize_modified_dict_if_necessary()
        if isinstance(value, dict):
            if value:
                for i in value:
                    self[key][i] = value[i]
            else:
                if key not in self.modified_dict or not isinstance(
                    self.modified_dict[key], dict
                ):
                    self.modified_dict[key] = value
            if (
                self.deleted_dict is not None
                and key in self.deleted_dict
                and self.deleted_dict[key] is None
            ):
                del self.deleted_dict[key]
                self.deinitialize_deleted_dict_if_necessary()
        else:
            self.modified_dict[key] = value
            if self.deleted_dict is not None:
                self.deleted_dict.pop(key, None)
                self.deinitialize_deleted_dict_if_necessary()

    def __delitem__(self, key):
        self.initialize_deleted_dict_if_necessary()
        self.deleted_dict[key] = None
        if self.modified_dict is not None:
            self.modified_dict.pop(key, None)
            # self.deinitialize_modified_dict_if_necessary()

    def copy(self):
        if self.modified_dict is not None:
            modified_dict = deepcopy(self.modified_dict)
        else:
            modified_dict = {}

        if self.deleted_dict is not None:
            deleted_dict = deepcopy(self.deleted_dict)
        else:
            deleted_dict = {}

        return modified_dict, deleted_dict


def delta_json_is_dict(delta_json):
    return isinstance(delta_json.modified_dict, dict)


def base_json_is_dict(base_json):
    return (
        isinstance(base_json, ConstJson) and isinstance(base_json.json_obj, dict)
    ) or isinstance(base_json, JsonWithDelta)


def apply_delta_json_on_base_obj(base_obj, delta_json):
    modified_dict, deleted_dict = delta_json.copy()

    stk = []
    stk.append((base_obj, modified_dict))
    while len(stk):
        cur_obj, cur_modified = stk.pop()
        for key in cur_modified:
            value = cur_modified[key]
            if isinstance(value, dict):
                if key not in cur_obj or not isinstance(cur_obj[key], dict):
                    cur_obj[key] = {}
                stk.append((cur_obj[key], value))
            else:
                cur_obj[key] = value

    stk = []
    stk.append((base_obj, deleted_dict))
    while len(stk):
        cur_obj, cur_deleted = stk.pop()
        for key in cur_deleted:
            value = cur_deleted[key]
            if isinstance(value, dict):
                stk.append((cur_obj[key], value))
            else:
                if key in cur_obj:
                    del cur_obj[key]

    return modified_dict, deleted_dict


def convert_deleted_dict_to_hg_format(deleted_dict):
    hg_deleted_dict = {}

    stk = []
    stk.append((deleted_dict, hg_deleted_dict))
    while len(stk):
        cur_deleted, cur_hg_deleted = stk.pop()
        for key in cur_deleted:
            value = cur_deleted[key]

            deleted_keys = []
            for i in value:
                if value[i] is None:
                    deleted_keys.append(i)

            if deleted_keys:
                cur_hg_deleted[key] = deleted_keys
                for i in deleted_keys:
                    del value[i]
            else:
                cur_hg_deleted[key] = {}
                stk.append((value, cur_hg_deleted[key]))

    stk = []
    for key in deleted_dict:
        stk.append((deleted_dict, key, 1))
    while len(stk):
        cur_deleted, cur_key, flag = stk.pop()
        if flag:
            stk.append((cur_deleted, cur_key, 0))
            value = cur_deleted[cur_key]
            if value is not None:
                for key in value:
                    stk.append((value, key, 1))
        else:
            if cur_deleted[cur_key] == {}:
                del cur_deleted[cur_key]

    return hg_deleted_dict


# always a dict-like object
class JsonWithDeltaIter:
    def __init__(self, json_with_delta):
        self.json_with_delta = json_with_delta

        self.iter_lst_idx = 0

        self.iter_set = set()

        if base_json_is_dict(json_with_delta.base_json):
            for i, j in json_with_delta.base_json:
                self.iter_set.add(i)

        if isinstance(json_with_delta.delta_json.modified_dict, dict):
            for i in json_with_delta.delta_json.modified_dict:
                self.iter_set.add(i)

        if isinstance(json_with_delta.delta_json.deleted_dict, dict):
            for i in json_with_delta.delta_json.deleted_dict:
                if i in self.iter_set:
                    self.iter_set.remove(i)

        self.iter_lst = list(self.iter_set)

    def __next__(self):
        if self.iter_lst_idx >= len(self.iter_lst):
            raise StopIteration
        key = self.iter_lst[self.iter_lst_idx]
        self.iter_lst_idx += 1
        return key, self.json_with_delta[key]


class JsonWithDelta:
    def __init__(
        self,
        base_json,
        delta_json,
    ):
        # ConstJson or JsonWithDelta or other non-dict object
        self.base_json = base_json
        # DeltaJson object
        self.delta_json = delta_json

    def __contains__(self, key):
        delta_json_status = self.delta_json.contains(key)
        return (
            base_json_is_dict(self.base_json)
            and key in self.base_json
            and delta_json_status != -1
        ) or delta_json_status == 1

    def __getitem__(self, key):
        if key not in self:
            raise KeyError

        if base_json_is_dict(self.base_json) and key in self.base_json:
            child_base_json = self.base_json[key]
        else:
            child_base_json = None

        child_delta_json = self.delta_json[key]

        if child_delta_json.no_dict:
            if isinstance(child_delta_json.no_dict_val, list):
                return ConstJson(child_delta_json.no_dict_val)
            return child_delta_json.no_dict_val

        if not base_json_is_dict(child_base_json) and not delta_json_is_dict(
            child_delta_json
        ):
            return child_base_json

        child_json_with_delta = JsonWithDelta(child_base_json, child_delta_json)

        return child_json_with_delta

    def __setitem__(self, key, value):
        self.delta_json[key] = value

    def __delitem__(self, key):
        if key not in self:
            raise KeyError

        del self.delta_json[key]

    def __iter__(self):
        json_with_delta_iter = JsonWithDeltaIter(self)
        return json_with_delta_iter

    def copy(self):
        if base_json_is_dict(self.base_json):
            base_obj = self.base_json.copy()
        else:
            base_obj = {}

        apply_delta_json_on_base_obj(base_obj, self.delta_json)

        return base_obj


class ResettableDeltaJson(DeltaJson):
    def reset(self):
        self.modified_dict = {}
        self.deleted_dict = {}

    def reset_key(self, key):
        if key in self.modified_dict:
            del self.modified_dict[key]

        if key in self.deleted_dict:
            del self.deleted_dict[key]


class FileBasedDeltaJson(ResettableDeltaJson):
    def __init__(self, path: str):
        self.path = path
        json_obj = load_delta_json_obj(path)

        super().__init__(
            modified_dict=json_obj["modified"], deleted_dict=json_obj["deleted"]
        )

    def save(self):
        save_delta_json_obj(self.path, self.modified_dict, self.deleted_dict)


class DBBasedDeltaJson(ResettableDeltaJson):
    def __init__(self, column_name: str, username: str):
        self.column_name = column_name
        self.username = username

        create_user_if_necessary(self.username)

        json_obj = self.load_delta_json_obj_from_db()
        if not json_obj:
            json_obj = {"modified": {}, "deleted": {}}

        super().__init__(
            modified_dict=json_obj["modified"], deleted_dict=json_obj["deleted"]
        )

    def load_delta_json_obj_from_db(self):
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT {self.column_name} FROM player_data WHERE username = %s",
                    (self.username,),
                )
                return cur.fetchone()[0]

    def save(self):
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE player_data SET {self.column_name} = %s WHERE username = %s",
                    (
                        Json(
                            {
                                "modified": self.modified_dict,
                                "deleted": self.deleted_dict,
                            }
                        ),
                        self.username,
                    ),
                )
                conn.commit()


class PlayerData(JsonWithDelta):
    def __init__(self, player_id=None):
        if flask.has_request_context():
            token = request.headers.get("secret", "")
        else:
            if player_id is not None:
                token = player_id
            else:
                token = ""
        self.username = get_username_by_token(token)

        config = const_json_loader[CONFIG_JSON]
        if config["multi_user"]:
            if IS_DB_READY:
                self.sav_delta_json = DBBasedDeltaJson(
                    "delta",
                    self.username,
                )
                self.sav_pending_delta_json = DBBasedDeltaJson(
                    "pending_delta",
                    self.username,
                )
                self.battle_replay_manager = DBBattleReplayManager(
                    self.username,
                )
                self.extra_save = DBExtraSave(self.username)
            else:
                self.sav_delta_json = FileBasedDeltaJson(
                    os.path.join(MULTI_USER_SAV_DIRPATH, self.username, "delta.json")
                )
                self.sav_pending_delta_json = FileBasedDeltaJson(
                    os.path.join(
                        MULTI_USER_SAV_DIRPATH, self.username, "pending_delta.json"
                    )
                )
                self.battle_replay_manager = BattleReplayManager(
                    os.path.join(MULTI_REPLAY_DIRPATH, self.username)
                )
                self.extra_save = ExtraSave(
                    os.path.join(MULTI_EXTRA_SAVE_DIRPATH, self.username, "extra.json")
                )
        else:
            self.sav_delta_json = FileBasedDeltaJson(SAV_DELTA_JSON)
            self.sav_pending_delta_json = FileBasedDeltaJson(SAV_PENDING_DELTA_JSON)
            self.battle_replay_manager = BattleReplayManager(REPLAY_DIRPATH)
            self.extra_save = ExtraSave(EXTRA_SAVE_FILEPATH)

        self.json_with_delta = JsonWithDelta(player_data_template, self.sav_delta_json)
        super().__init__(self.json_with_delta, self.sav_pending_delta_json)

    def save(self):
        self.sav_delta_json.save()
        self.sav_pending_delta_json.save()
        self.extra_save.save()

    def reset(self):
        self.sav_delta_json.reset()
        self.sav_pending_delta_json.reset()
        self.extra_save.reset()

    def reset_key(self, key):
        self.sav_delta_json.reset_key(key)
        self.sav_pending_delta_json.reset_key(key)

    def build_delta_response(self):
        modified_dict, deleted_dict = apply_delta_json_on_base_obj(
            self.json_with_delta, self.sav_pending_delta_json
        )
        self.sav_pending_delta_json.reset()
        hg_deleted_dict = convert_deleted_dict_to_hg_format(deleted_dict)
        self.sav_pending_delta_json.deleted_dict = deleted_dict
        return {"modified": modified_dict, "deleted": hg_deleted_dict}


def player_data_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        player_data = PlayerData()
        json_response = func(player_data, *args, **kwargs)

        if not isinstance(json_response, dict):
            return json_response

        # --- message  ---
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

                break

        delta_response = player_data.build_delta_response()
        player_data.save()

        json_response["playerDataDelta"] = delta_response

        if const_json_loader[CONFIG_JSON]["debug"]:
            delta_response_str = json.dumps(delta_response, ensure_ascii=False)
            if flask.has_app_context():
                flask.current_app.logger.debug(delta_response_str)
            else:
                print(delta_response_str)

        return json_response

    return wrapper
