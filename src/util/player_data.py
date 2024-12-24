from copy import deepcopy

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
    DISPLAY_META_TABLE,
    MEDAL_TABLE,
    STORY_REVIEW_TABLE,
    STORY_REVIEW_META_TABLE,
    ENEMY_HANDBOOK_TABLE,
    ACTIVITY_TABLE,
    SAV_DELTA_JSON,
    SAV_PENDING_DELTA_JSON,
)
from .const_json_loader import const_json_loader, ConstJson
from .helper import (
    is_char_id,
    get_char_num_id,
    load_delta_json_obj,
    save_delta_json_obj,
    merge_delta_into_tmpl,
)


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

    player_data_template = ConstJson(tmpl_json_obj)
    return player_data_template


player_data_template = build_player_data_template()


class MissingJsonObj:
    pass


class DeltaJson:
    def __init__(
        self,
        modified_json_obj,
        deleted_json_obj,
        parent=None,
        prev_key=None,
    ):
        if parent is None:
            modified_json_obj = deepcopy(modified_json_obj)
            deleted_json_obj = deepcopy(deleted_json_obj)
        self.modified_json_obj = modified_json_obj
        self.deleted_json_obj = deleted_json_obj
        self.parent = parent
        self.prev_key = prev_key

    def update_parent(self):
        if self.parent is not None:
            if isinstance(self.modified_json_obj, MissingJsonObj):
                if not isinstance(self.parent.modified_json_obj, MissingJsonObj):
                    self.parent.modified_json_obj.pop(self.prev_key, None)
            else:
                self.parent.modified_json_obj[self.prev_key] = self.modified_json_obj

            if isinstance(self.deleted_json_obj, MissingJsonObj):
                if not isinstance(self.parent.deleted_json_obj, MissingJsonObj):
                    self.parent.deleted_json_obj.pop(self.prev_key, None)
            else:
                self.parent.deleted_json_obj[self.prev_key] = self.deleted_json_obj

    def format(self):
        if self.parent is not None:
            if not self.deleted_json_obj:
                self.deleted_json_obj = MissingJsonObj()
            self.update_parent()
            self.parent.format()

    def create_modified_if_necessary(self):
        if self.parent is not None:
            self.parent.create_modified_if_necessary()
        if not isinstance(self.modified_json_obj, dict):
            self.modified_json_obj = {}
            self.update_parent()

    def create_deleted_if_necessary(self, is_last=False):
        if self.parent is not None:
            self.parent.create_deleted_if_necessary()
        if is_last:
            target_type = list
        else:
            target_type = dict
        if not isinstance(self.deleted_json_obj, target_type):
            if is_last:
                self.deleted_json_obj = []
            else:
                self.deleted_json_obj = {}
            self.update_parent()

    def __getitem__(self, key):
        if isinstance(self.modified_json_obj, dict) and key in self.modified_json_obj:
            child_modified_json_obj = self.modified_json_obj[key]
        else:
            child_modified_json_obj = MissingJsonObj()

        if isinstance(self.deleted_json_obj, dict) and key in self.deleted_json_obj:
            child_deleted_json_obj = self.deleted_json_obj[key]
        else:
            child_deleted_json_obj = MissingJsonObj()

        child_delta_json = DeltaJson(
            child_modified_json_obj,
            child_deleted_json_obj,
            parent=self,
            prev_key=key,
        )

        return child_delta_json

    def __setitem__(self, key, value):
        value = deepcopy(value)

        self.create_modified_if_necessary()

        self.modified_json_obj[key] = value

        if isinstance(self.deleted_json_obj, dict) and key in self.deleted_json_obj:
            del self.deleted_json_obj[key]

        if isinstance(self.deleted_json_obj, list) and key in self.deleted_json_obj:
            self.deleted_json_obj.remove(key)

        self.format()

    def __delitem__(self, key):
        self.create_deleted_if_necessary(is_last=True)

        self.deleted_json_obj.append(key)

        if isinstance(self.modified_json_obj, dict) and key in self.modified_json_obj:
            del self.modified_json_obj[key]

    def contains(self, key):
        if isinstance(self.modified_json_obj, dict) and key in self.modified_json_obj:
            return 1
        if (
            not isinstance(self.deleted_json_obj, MissingJsonObj)
            and key in self.deleted_json_obj
        ):
            return -1
        return 0

    def copy(self):
        if not isinstance(self.modified_json_obj, MissingJsonObj):
            modified_json_obj_copy = deepcopy(self.modified_json_obj)
        else:
            modified_json_obj_copy = {}
        if not isinstance(self.deleted_json_obj, MissingJsonObj):
            deleted_json_obj_copy = deepcopy(self.deleted_json_obj)
        else:
            deleted_json_obj_copy = {}

        return modified_json_obj_copy, deleted_json_obj_copy


class JsonWithDeltaIter:
    def __init__(self, json_with_delta):
        self.json_with_delta = json_with_delta

        self.iter_lst_idx = 0

        self.iter_set = set()

        if json_with_delta.base_json_is_custom_type():
            for i, j in json_with_delta.base_json:
                self.iter_set.add(i)

        if isinstance(json_with_delta.delta_json.modified_json_obj, dict):
            for i in json_with_delta.delta_json.modified_json_obj:
                self.iter_set.add(i)

        if isinstance(json_with_delta.delta_json.deleted_json_obj, list):
            for i in json_with_delta.delta_json.deleted_json_obj:
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
    def __init__(self, base_json, delta_json):
        self.base_json = base_json
        self.delta_json = delta_json

    def base_json_is_custom_type(self):
        return isinstance(self.base_json, ConstJson) or isinstance(
            self.base_json, JsonWithDelta
        )

    def base_json_contains(self, key):
        return self.base_json_is_custom_type() and key in self.base_json

    def self_is_dict(self):
        return (
            self.base_json_is_custom_type()
            and isinstance(self.delta_json.modified_json_obj, MissingJsonObj)
        ) or isinstance(self.delta_json.modified_json_obj, dict)

    def __contains__(self, key):
        delta_json_key_stats = self.delta_json.contains(key)
        if (
            self.base_json_contains(key) and delta_json_key_stats != -1
        ) or delta_json_key_stats == 1:
            return True
        return False

    def __getitem__(self, key):
        if key not in self:
            raise KeyError

        if self.base_json_contains(key):
            child_base_json = self.base_json[key]
        else:
            child_base_json = None

        child_delta_json = self.delta_json[key]

        child_json_with_delta = JsonWithDelta(child_base_json, child_delta_json)

        return child_json_with_delta

    def __setitem__(self, key, value):
        if not self.self_is_dict():
            raise TypeError

        self.delta_json[key] = value

    def __delitem__(self, key):
        if key not in self:
            raise KeyError

        del self.delta_json[key]

    def copy(self):
        if self.base_json_is_custom_type():
            json_obj = self.base_json.copy()
        else:
            json_obj = self.base_json
        modified_json_obj_copy, deleted_json_obj_copy = self.delta_json.copy()

        if not isinstance(modified_json_obj_copy, dict):
            return modified_json_obj_copy
        if not isinstance(json_obj, dict) and not modified_json_obj_copy:
            return json_obj

        merge_delta_into_tmpl(json_obj, modified_json_obj_copy, deleted_json_obj_copy)

        return json_obj

    def __iter__(self):
        if not self.self_is_dict():
            raise TypeError
        json_with_delta_iter = JsonWithDeltaIter(self)
        return json_with_delta_iter


class FileBasedDeltaJson(DeltaJson):
    def __init__(self, path: str):
        self.path = path
        json_obj = load_delta_json_obj(path)

        super().__init__(json_obj["modified"], json_obj["deleted"])

    def save(self):
        save_delta_json_obj(self.path, self.modified_json_obj, self.deleted_json_obj)

    def reset(self):
        self.modified_json_obj = {}
        self.deleted_json_obj = {}


class PlayerData:
    def __init__(self):
        self.sav_delta_json = FileBasedDeltaJson(SAV_DELTA_JSON)
        self.sav_pending_delta_json = FileBasedDeltaJson(SAV_PENDING_DELTA_JSON)
        self.json_with_delta = JsonWithDelta(player_data_template, self.sav_delta_json)
        self.json_with_delta_delta = JsonWithDelta(
            player_data_template, self.sav_pending_delta_json
        )

    def accessor(self):
        return self.json_with_delta_delta

    def save(self):
        self.sav_delta_json.save()
        self.sav_pending_delta_json.save()

    def reset(self):
        self.sav_delta_json.reset()
        self.sav_pending_delta_json.reset()
