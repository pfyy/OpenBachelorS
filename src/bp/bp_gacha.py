from enum import IntEnum
import random

from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import (
    CONFIG_JSON,
    VERSION_JSON,
    CHARACTER_TABLE,
    GACHA_POOL_JSON,
    GACHA_TABLE,
    GACHA_DATA,
)
from ..util.const_json_loader import const_json_loader, ConstJson
from ..util.player_data import player_data_decorator, char_id_lst as player_char_id_lst
from ..util.helper import (
    get_char_num_id,
    get_random_key,
    get_char_str_tag_lst,
)
from ..util.faketime import faketime

bp_gacha = Blueprint("bp_gacha", __name__)


@bp_gacha.route("/gacha/syncNormalGacha", methods=["POST"])
@player_data_decorator
def gacha_syncNormalGacha(player_data):
    request_json = request.get_json()
    response = {}
    return response


def get_gacha_bonus_item(char_id):
    char_rarity_str = const_json_loader[CHARACTER_TABLE][char_id]["rarity"]

    if char_rarity_str == "TIER_6":
        gacha_bonus_item = {"type": "HGG_SHD", "id": "4004", "count": 15}
    elif char_rarity_str == "TIER_5":
        gacha_bonus_item = {"type": "HGG_SHD", "id": "4004", "count": 8}
    elif char_rarity_str == "TIER_4":
        gacha_bonus_item = {"type": "HGG_SHD", "id": "4004", "count": 30}
    elif char_rarity_str == "TIER_3":
        gacha_bonus_item = {"type": "LGG_SHD", "id": "4005", "count": 5}
    elif char_rarity_str == "TIER_2":
        gacha_bonus_item = {"type": "LGG_SHD", "id": "4005", "count": 1}
    else:
        gacha_bonus_item = {"type": "LGG_SHD", "id": "4005", "count": 1}

    return gacha_bonus_item


def get_gacha_char_obj(char_id):
    character_table = const_json_loader[CHARACTER_TABLE]
    item_id = character_table[char_id]["potentialItemId"]

    gacha_bonus_item = get_gacha_bonus_item(char_id)

    gacha_char_obj = {
        "charInstId": get_char_num_id(char_id),
        "charId": char_id,
        "isNew": 0,
        "itemGet": [
            gacha_bonus_item,
            {"type": "MATERIAL", "id": item_id, "count": 1},
        ],
        "logInfo": {},
    }

    return gacha_char_obj


class NormalGachaBasicManager:
    def __init__(self, player_data, request_json, response):
        self.player_data = player_data
        self.request_json = request_json
        self.response = response

        self.slot_id = self.request_json["slotId"]

    # override this
    def get_refreshed_tag_lst(self):
        refreshed_tag_lst = [11, 2, 10, 19]
        return refreshed_tag_lst

    def refresh_tag_lst(self):
        refreshed_tag_lst = self.get_refreshed_tag_lst()
        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)]["tags"] = (
            refreshed_tag_lst
        )

    def gacha_normalGacha(self):
        t = int(faketime())

        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)]["state"] = 2

        selected_tag_lst = []
        for tag_id in self.request_json["tagList"]:
            selected_tag_lst.append({"tagId": tag_id, "pick": 0})
        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)][
            "selectTags"
        ] = selected_tag_lst

        duration = self.request_json["duration"]
        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)]["startTs"] = t
        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)][
            "durationInSec"
        ] = duration
        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)][
            "maxFinishTs"
        ] = t + duration
        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)][
            "realFinishTs"
        ] = t + duration

        self.refresh_tag_lst()

    # override this
    def get_gacha_raw_result(self):
        char_id = "char_1035_wisdel"
        picked_tag_lst = [11, 2, 10, 19]

        return char_id, picked_tag_lst

    def exec_gacha(self):
        char_id, picked_tag_lst = self.get_gacha_raw_result()

        selected_tag_lst = self.player_data["recruit"]["normal"]["slots"][
            str(self.slot_id)
        ]["selectTags"].copy()

        for selected_tag in selected_tag_lst:
            selected_tag_id = selected_tag["tagId"]
            if selected_tag_id in picked_tag_lst:
                selected_tag["pick"] = 1

        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)][
            "selectTags"
        ] = selected_tag_lst

        self.player_data.extra_save.save_obj[f"normal_gacha_{self.slot_id}"] = char_id

    def get_gacha_result(self):
        k = f"normal_gacha_{self.slot_id}"
        if not self.player_data.extra_save.save_obj.get(k):
            self.exec_gacha()

        return self.player_data.extra_save.save_obj.get(k)

    def clear_gacha_result(self):
        self.player_data.extra_save.save_obj[f"normal_gacha_{self.slot_id}"] = None

    def gacha_boostNormalGacha(self):
        t = int(faketime())

        self.get_gacha_result()

        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)]["state"] = 3

        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)][
            "realFinishTs"
        ] = t

        self.response.update(
            {
                "result": 0,
            }
        )

    def reset_slot(self):
        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)]["state"] = 1

        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)][
            "selectTags"
        ] = []

        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)][
            "startTs"
        ] = -1
        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)][
            "durationInSec"
        ] = -1
        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)][
            "maxFinishTs"
        ] = -1
        self.player_data["recruit"]["normal"]["slots"][str(self.slot_id)][
            "realFinishTs"
        ] = -1

    def gacha_finishNormalGacha(self):
        char_id = self.get_gacha_result()
        self.clear_gacha_result()

        gacha_char_obj = get_gacha_char_obj(char_id)

        self.reset_slot()

        self.response.update(
            {
                "result": 0,
                "charGet": gacha_char_obj,
            }
        )

    def gacha_cancelNormalGacha(self):
        self.reset_slot()

        self.response.update(
            {
                "result": 0,
            }
        )

    def gacha_refreshTags(self):
        self.refresh_tag_lst()


def build_tag_id_char_id_set_dict():
    tag_id_char_id_set_dict = {}

    str_tag_tag_id_dict = {}

    gacha_table = const_json_loader[GACHA_TABLE]

    for i, tag_obj in gacha_table["gachaTags"]:
        tag_id = tag_obj["tagId"]
        str_tag = tag_obj["tagName"]
        str_tag_tag_id_dict[str_tag] = tag_id

    character_table = const_json_loader[CHARACTER_TABLE]
    for i, char_id in player_char_id_lst:
        char_obj = character_table[char_id]
        str_tag_lst = get_char_str_tag_lst(char_obj)

        for str_tag in str_tag_lst:
            if str_tag in str_tag_tag_id_dict:
                tag_id = str_tag_tag_id_dict[str_tag]
                if tag_id not in tag_id_char_id_set_dict:
                    tag_id_char_id_set_dict[tag_id] = set()
                tag_id_char_id_set_dict[tag_id].add(char_id)

    valid_tag_id_lst = list(tag_id_char_id_set_dict.keys())

    return tag_id_char_id_set_dict, valid_tag_id_lst


tag_id_char_id_set_dict, valid_tag_id_lst = build_tag_id_char_id_set_dict()


class NormalGachaSimpleManager(NormalGachaBasicManager):
    def get_refreshed_tag_lst(self):
        refreshed_tag_lst = random.sample(valid_tag_id_lst, 5)
        return refreshed_tag_lst

    def get_raw_tag_lst(self):
        raw_tag_lst = []
        for i, tag_obj in self.player_data["recruit"]["normal"]["slots"][
            str(self.slot_id)
        ]["selectTags"]:
            raw_tag_lst.append(tag_obj["tagId"])

        return raw_tag_lst

    def get_gacha_raw_result(self):
        picked_tag_lst = []

        raw_tag_lst = self.get_raw_tag_lst()
        random.shuffle(raw_tag_lst)

        char_id_set = set(player_char_id_lst.copy())

        for tag_id in raw_tag_lst:
            tmp_char_id_set = char_id_set.intersection(tag_id_char_id_set_dict[tag_id])

            if not tmp_char_id_set:
                break

            picked_tag_lst.append(tag_id)
            char_id_set = tmp_char_id_set

        char_id = random.choice(list(char_id_set))

        return char_id, picked_tag_lst


def get_normal_gacha_manager(player_data, request_json, response):
    return NormalGachaSimpleManager(player_data, request_json, response)


@bp_gacha.route("/gacha/normalGacha", methods=["POST"])
@player_data_decorator
def gacha_normalGacha(player_data):
    request_json = request.get_json()
    response = {}

    normal_gacha_manager = get_normal_gacha_manager(player_data, request_json, response)
    normal_gacha_manager.gacha_normalGacha()

    return response


@bp_gacha.route("/gacha/boostNormalGacha", methods=["POST"])
@player_data_decorator
def gacha_boostNormalGacha(player_data):
    request_json = request.get_json()
    response = {}

    normal_gacha_manager = get_normal_gacha_manager(player_data, request_json, response)
    normal_gacha_manager.gacha_boostNormalGacha()

    return response


@bp_gacha.route("/gacha/finishNormalGacha", methods=["POST"])
@player_data_decorator
def gacha_finishNormalGacha(player_data):
    request_json = request.get_json()
    response = {}

    normal_gacha_manager = get_normal_gacha_manager(player_data, request_json, response)
    normal_gacha_manager.gacha_finishNormalGacha()

    return response


@bp_gacha.route("/gacha/cancelNormalGacha", methods=["POST"])
@player_data_decorator
def gacha_cancelNormalGacha(player_data):
    request_json = request.get_json()
    response = {}

    normal_gacha_manager = get_normal_gacha_manager(player_data, request_json, response)
    normal_gacha_manager.gacha_cancelNormalGacha()

    return response


@bp_gacha.route("/gacha/refreshTags", methods=["POST"])
@player_data_decorator
def gacha_refreshTags(player_data):
    request_json = request.get_json()
    response = {}

    normal_gacha_manager = get_normal_gacha_manager(player_data, request_json, response)
    normal_gacha_manager.gacha_refreshTags()

    return response


GACHA_RULE_TYPE_DICT = ConstJson(
    {
        "NORMAL": "normal",
        "ATTAIN": "attain",
        "LIMITED": "limit",
        "SINGLE": "single",
        "FESCLASSIC": "fesClassic",
        "LINKAGE": "linkage",
        "SPECIAL": "special",
        "DOUBLE": "double",
        "CLASSIC": "normal",
        "CLASSIC_ATTAIN": "attain",
        "CLASSIC_DOUBLE": "double",
    }
)


def init_pool_id_gacha_type_dict():
    pool_id_gacha_type_dict = {}
    pool_id_is_classic_dict = {}
    gacha_table = const_json_loader[GACHA_TABLE]

    for i, gacha_obj in gacha_table["gachaPoolClient"]:
        pool_id = gacha_obj["gachaPoolId"]
        gacha_rule_type = gacha_obj["gachaRuleType"]
        if gacha_rule_type in GACHA_RULE_TYPE_DICT:
            gacha_type = GACHA_RULE_TYPE_DICT[gacha_rule_type]

            pool_id_gacha_type_dict[pool_id] = gacha_type
            pool_id_is_classic_dict[pool_id] = "CLASSIC" in gacha_rule_type

    for i, newbee_gacha_obj in gacha_table["newbeeGachaPoolClient"]:
        pool_id = newbee_gacha_obj["gachaPoolId"]
        pool_id_gacha_type_dict[pool_id] = "newbee"
        pool_id_is_classic_dict[pool_id] = True

    return ConstJson(pool_id_gacha_type_dict), ConstJson(pool_id_is_classic_dict)


pool_id_gacha_type_dict, pool_id_is_classic_dict = init_pool_id_gacha_type_dict()


class CharRarityRank(IntEnum):
    TIER_6 = 5
    TIER_5 = 4
    TIER_4 = 3
    TIER_3 = 2


class AdvancedGachaBasicManager:
    def __init__(self, player_data, request_json, response, pool_id, gacha_type):
        self.player_data = player_data
        self.request_json = request_json
        self.response = response

        self.pool_id = pool_id

        self.gacha_type = gacha_type

        self.is_classic = pool_id_is_classic_dict[pool_id]

    # override this
    def get_advanced_gacha_result(self):
        char_id = "char_1035_wisdel"

        return char_id

    def gacha_advancedGacha(self):
        char_id = self.get_advanced_gacha_result()

        gacha_char_obj = get_gacha_char_obj(char_id)

        self.response.update(
            {
                "result": 0,
                "charGet": gacha_char_obj,
            }
        )

    def gacha_tenAdvancedGacha(self):
        char_id_lst = [self.get_advanced_gacha_result() for i in range(10)]

        gacha_char_obj_lst = [get_gacha_char_obj(char_id) for char_id in char_id_lst]

        self.response.update(
            {
                "result": 0,
                "gachaResultList": gacha_char_obj_lst,
            }
        )

    # override this
    def gacha_getPoolDetail(self):
        gacha_pool = const_json_loader[GACHA_POOL_JSON]

        self.response.update(gacha_pool.copy())

    def gacha_choosePoolUp(self):
        self.player_data["gacha"][self.gacha_type][self.pool_id] = {
            "upChar": self.request_json["chooseChar"]
        }
        self.response.update(
            {
                "result": 0,
            }
        )


class AdvancedGachaSimpleManager(AdvancedGachaBasicManager):
    def get_basic_tier_6_pity_key(self):
        if self.is_classic:
            return "advanced_gacha_classic_basic_tier_6_pity"
        else:
            return "advanced_gacha_normal_basic_tier_6_pity"

    def get_basic_tier_6_pity(self):
        basic_tier_6_pity_key = self.get_basic_tier_6_pity_key()

        return self.player_data.extra_save.save_obj.get(basic_tier_6_pity_key, 0)

    def set_basic_tier_6_pity(self, basic_tier_6_pity):
        basic_tier_6_pity_key = self.get_basic_tier_6_pity_key()
        self.player_data.extra_save.save_obj[basic_tier_6_pity_key] = basic_tier_6_pity

    BASIC_TIER_6_PITY_THRESHOLD = 50
    BASIC_TIER_6_PITY_PERCENT = 0.02

    def get_actual_tier_6_percent(self, orig_tier_6_percent):
        if not orig_tier_6_percent:
            return orig_tier_6_percent
        basic_tier_6_pity = self.get_basic_tier_6_pity()
        if basic_tier_6_pity < self.BASIC_TIER_6_PITY_THRESHOLD:
            return orig_tier_6_percent
        return orig_tier_6_percent + self.BASIC_TIER_6_PITY_PERCENT * (
            basic_tier_6_pity - self.BASIC_TIER_6_PITY_THRESHOLD + 1
        )

    def get_avail_char_info(self):
        gacha_data = const_json_loader[GACHA_DATA]
        if self.is_classic:
            return gacha_data["classic_avail_char_info"]
        else:
            return gacha_data["normal_avail_char_info"]

    def get_up_char_info(self):
        gacha_data = const_json_loader[GACHA_DATA]
        if self.pool_id in gacha_data["up_char_info"]:
            return gacha_data["up_char_info"][self.pool_id]
        return ConstJson({})

    def get_char_rarity_rank(self):
        avail_char_info = self.get_avail_char_info()
        char_rarity_rank_percent_dict = {}

        for char_rarity_rank in CharRarityRank:
            if char_rarity_rank.name in avail_char_info:
                char_rarity_rank_percent = avail_char_info[char_rarity_rank.name][
                    "total_percent"
                ]
            else:
                char_rarity_rank_percent = 0

            char_rarity_rank_percent_dict[char_rarity_rank] = char_rarity_rank_percent

        orig_tier_6_percent = char_rarity_rank_percent_dict[CharRarityRank.TIER_6]
        actual_tier_6_percent = self.get_actual_tier_6_percent(orig_tier_6_percent)
        char_rarity_rank_percent_dict[CharRarityRank.TIER_6] = actual_tier_6_percent

        char_rarity_rank = get_random_key(char_rarity_rank_percent_dict)

        if char_rarity_rank is None:
            char_rarity_rank = CharRarityRank.TIER_3

        return char_rarity_rank

    def get_up_char_id_if_lucky(self, char_rarity_rank):
        up_char_info = self.get_up_char_info()

        if char_rarity_rank.name not in up_char_info:
            return None

        up_char_id_percent_dict = {}
        for i, char_id in up_char_info[char_rarity_rank.name]["char_id_lst"]:
            up_char_id_percent_dict[char_id] = up_char_info[char_rarity_rank.name][
                "percent"
            ]

        return get_random_key(up_char_id_percent_dict)

    def get_avail_char_id_lst(self, char_rarity_rank):
        avail_char_info = self.get_avail_char_info()
        avail_char_id_lst = avail_char_info[char_rarity_rank.name]["char_id_lst"].copy()
        return avail_char_id_lst

    def get_avail_char_id(self, char_rarity_rank):
        avail_char_id_lst = self.get_avail_char_id_lst(char_rarity_rank)

        return random.choice(avail_char_id_lst)

    def get_gacha_num(self):
        return self.player_data.extra_save.save_obj.get(
            f"advanced_gacha_num_{self.pool_id}", 0
        )

    def set_gacha_num(self, gacha_num):
        self.player_data.extra_save.save_obj[f"advanced_gacha_num_{self.pool_id}"] = (
            gacha_num
        )

    BASIC_TIER_5_PITY_THRESHOLD = 10

    def get_basic_tier_5_pity_key(self):
        return f"advanced_gacha_basic_tier_5_pity_{self.pool_id}"

    def get_basic_tier_5_pity(self):
        basic_tier_5_pity_key = self.get_basic_tier_5_pity_key()

        return self.player_data.extra_save.save_obj.get(basic_tier_5_pity_key, False)

    def set_basic_tier_5_pity(self):
        basic_tier_5_pity_key = self.get_basic_tier_5_pity_key()
        self.player_data.extra_save.save_obj[basic_tier_5_pity_key] = True

    def post_gacha_operations(self, char_rarity_rank, char_id):
        if char_rarity_rank == CharRarityRank.TIER_6:
            basic_tier_6_pity = 0
        else:
            basic_tier_6_pity = self.get_basic_tier_6_pity() + 1

        self.set_basic_tier_6_pity(basic_tier_6_pity)

        gacha_num = self.get_gacha_num() + 1
        self.set_gacha_num(gacha_num)

        if char_rarity_rank >= CharRarityRank.TIER_5:
            self.set_basic_tier_5_pity()

        if self.pool_id not in self.player_data["gacha"]["normal"]:
            self.player_data["gacha"]["normal"][self.pool_id] = {
                "cnt": 0,
                "maxCnt": 10,
                "rarity": 4,
                "avail": true,
            }

        self.player_data["gacha"]["normal"][self.pool_id]["cnt"] = gacha_num
        self.player_data["gacha"]["normal"][self.pool_id][
            "avail"
        ] = not self.get_basic_tier_5_pity()

    def pre_gacha_override(self):
        char_rarity_rank = None
        char_id = None

        gacha_num = self.get_gacha_num()

        if gacha_num + 1 == self.BASIC_TIER_5_PITY_THRESHOLD:
            basic_tier_5_pity = self.get_basic_tier_5_pity()

            if not basic_tier_5_pity:
                char_rarity_rank = CharRarityRank.TIER_5

        return char_rarity_rank, char_id

    def post_gacha_override(self, char_rarity_rank, char_id):
        return char_rarity_rank, char_id

    def get_advanced_gacha_result(self):
        char_rarity_rank, char_id = self.pre_gacha_override()

        if char_rarity_rank is None:
            char_rarity_rank = self.get_char_rarity_rank()

        if char_id is None:
            char_id = self.get_up_char_id_if_lucky(char_rarity_rank)

        if char_id is None:
            char_id = self.get_avail_char_id(char_rarity_rank)

        char_rarity_rank, char_id = self.post_gacha_override(char_rarity_rank, char_id)

        self.post_gacha_operations(char_rarity_rank, char_id)

        return char_id

    def gacha_getPoolDetail(self):
        avail_char_info = self.get_avail_char_info()

        per_avail_list = []

        for char_tier_name, char_tier_obj in avail_char_info:
            per_avail_list.append(
                {
                    "rarityRank": CharRarityRank[char_tier_name].value,
                    "charIdList": char_tier_obj["char_id_lst"].copy(),
                    "totalPercent": char_tier_obj["total_percent"],
                }
            )

        up_char_info = self.get_up_char_info()

        per_char_list = []
        for char_tier_name, char_tier_obj in up_char_info:
            per_char_list.append(
                {
                    "rarityRank": CharRarityRank[char_tier_name].value,
                    "charIdList": char_tier_obj["char_id_lst"].copy(),
                    "percent": char_tier_obj["percent"],
                    "count": len(char_tier_obj["char_id_lst"]),
                }
            )

        if self.is_classic:
            gacha_obj_list = [
                {
                    "gachaObject": "TEXT",
                    "type": 0,
                    "imageType": 0,
                    "param": "卡池干员列表",
                },
                {
                    "gachaObject": "RATE_UP_6",
                    "type": 0,
                    "imageType": 0,
                    "param": "中坚寻访",
                },
                {
                    "gachaObject": "TEXT",
                    "type": 2,
                    "imageType": 0,
                    "param": "出现概率上升",
                },
                {"gachaObject": "UP_CHAR", "type": 0, "imageType": 0, "param": null},
                {
                    "gachaObject": "TEXT",
                    "type": 1,
                    "imageType": 0,
                    "param": "全部可能出现的干员",
                },
                {"gachaObject": "AVAIL_CHAR", "type": 0, "imageType": 0, "param": null},
                {
                    "gachaObject": "TEXT",
                    "type": 0,
                    "imageType": 0,
                    "param": "该寻访为【中坚寻访】",
                },
            ]
        else:
            gacha_obj_list = [
                {
                    "gachaObject": "TEXT",
                    "type": 0,
                    "imageType": 0,
                    "param": "卡池干员列表",
                },
                {
                    "gachaObject": "RATE_UP_6",
                    "type": 0,
                    "imageType": 0,
                    "param": "标准寻访",
                },
                {
                    "gachaObject": "TEXT",
                    "type": 2,
                    "imageType": 0,
                    "param": "出现概率上升",
                },
                {"gachaObject": "UP_CHAR", "type": 0, "imageType": 0, "param": null},
                {
                    "gachaObject": "TEXT",
                    "type": 1,
                    "imageType": 0,
                    "param": "全部可能出现的干员",
                },
                {"gachaObject": "AVAIL_CHAR", "type": 0, "imageType": 0, "param": null},
                {
                    "gachaObject": "TEXT",
                    "type": 0,
                    "imageType": 0,
                    "param": "该寻访为【标准寻访】",
                },
            ]

        self.response.update(
            {
                "detailInfo": {
                    "gachaObjGroups": null,
                    "availCharInfo": {"perAvailList": per_avail_list},
                    "upCharInfo": {"perCharList": per_char_list},
                    "limitedChar": null,
                    "weightUpCharInfoList": null,
                    "gachaObjList": gacha_obj_list,
                },
                "gachaObjGroupType": 0,
                "hasRateUp": false,
            }
        )


class AdvancedGachaDoubleManager(AdvancedGachaSimpleManager):
    def __init__(self, player_data, request_json, response, pool_id, gacha_type):
        super().__init__(player_data, request_json, response, pool_id, gacha_type)

        up_char_info = self.get_up_char_info()

        self.is_valid_pool = True
        if (
            CharRarityRank.TIER_6.name not in up_char_info
            or len(up_char_info[CharRarityRank.TIER_6.name]["char_id_lst"]) != 2
        ):
            self.is_valid_pool = False

        if not self.is_valid_pool:
            print(f"warn: double pool {self.pool_id} misconfigured")

    def get_double_char_id_lst(self):
        double_char_id_lst_key = f"advanced_gacha_double_char_id_lst_{self.pool_id}"
        if double_char_id_lst_key not in self.player_data.extra_save.save_obj:
            up_char_info = self.get_up_char_info()
            char_id_lst = up_char_info[CharRarityRank.TIER_6.name]["char_id_lst"].copy()
            random.shuffle(char_id_lst)
            self.player_data.extra_save.save_obj[double_char_id_lst_key] = char_id_lst
        return self.player_data.extra_save.save_obj[double_char_id_lst_key]

    def get_is_x_taken_key(self, x):
        return f"advanced_gacha_is_{x}_taken_{self.pool_id}"

    def get_is_x_taken(self, x):
        is_x_taken_key = self.get_is_x_taken_key(x)

        return self.player_data.extra_save.save_obj.get(is_x_taken_key, False)

    def set_is_x_taken(self, x, is_x_taken):
        is_x_taken_key = self.get_is_x_taken_key(x)

        self.player_data.extra_save.save_obj[is_x_taken_key] = is_x_taken

    def post_gacha_override(self, char_rarity_rank, char_id):
        char_rarity_rank, char_id = super().post_gacha_override(
            char_rarity_rank, char_id
        )

        if not self.is_valid_pool:
            return char_rarity_rank, char_id

        gacha_num = self.get_gacha_num()

        if char_rarity_rank == CharRarityRank.TIER_6:
            if gacha_num >= 150 and not self.get_is_x_taken(0):
                char_id = self.get_double_char_id_lst()[0]
                self.set_is_x_taken(0, True)
            elif gacha_num >= 300 and not self.get_is_x_taken(1):
                char_id = self.get_double_char_id_lst()[1]
                self.set_is_x_taken(1, True)
        return char_rarity_rank, char_id

    def post_gacha_operations(self, char_rarity_rank, char_id):
        super().post_gacha_operations(char_rarity_rank, char_id)

        if not self.is_valid_pool:
            return

        if self.pool_id not in self.player_data["gacha"]["double"]:
            self.player_data["gacha"]["double"][self.pool_id] = {
                "showCnt": 0,
                "hitCharState": 0,
                "hitCharId": null,
            }

        gacha_num = self.get_gacha_num()

        if gacha_num < 300:
            self.player_data["gacha"]["double"][self.pool_id]["showCnt"] = gacha_num
        else:
            self.player_data["gacha"]["double"][self.pool_id]["showCnt"] = -1

        if gacha_num == 150:
            self.player_data["gacha"]["double"][self.pool_id]["hitCharState"] = 1
        elif gacha_num == 300:
            self.player_data["gacha"]["double"][self.pool_id]["hitCharState"] = 2
            self.player_data["gacha"]["double"][self.pool_id]["hitCharId"] = (
                self.get_double_char_id_lst()[1]
            )
        elif char_rarity_rank == CharRarityRank.TIER_6:
            self.player_data["gacha"]["double"][self.pool_id]["hitCharState"] = 0
            self.player_data["gacha"]["double"][self.pool_id]["hitCharId"] = null

    def gacha_getPoolDetail(self):
        super().gacha_getPoolDetail()

        gacha_obj_list = self.response["detailInfo"]["gachaObjList"]

        if self.is_classic:
            gacha_obj_list += [
                {
                    "gachaObject": "TEXT",
                    "type": 5,
                    "imageType": 0,
                    "param": "在所有<@ga.adGacha>【中坚寻访】</>中，如果连续<@ga.percent>50</>次没有获得6星干员，则下一次获得6星干员的概率将从原本的<@ga.percent>2%</>提升至<@ga.percent>4%</>。如果该次还没有寻访到6星干员，则下一次寻访获得6星的概率由<@ga.percent>4%</>提升到<@ga.percent>6%</>。依此类推，每次提高<@ga.percent>2%</>获得6星干员的概率，直至达到<@ga.percent>100%</>时必定获得6星干员。\n在任何一个<@ga.adGacha>【中坚寻访】</>中，没有获得6星干员时，都会累积次数，该次数不会因为<@ga.adGacha>【中坚寻访】</>的结束而清零。因为累积次数而增加的获得概率，也会应用于接下来任意一次<@ga.adGacha>【中坚寻访】</>。\n<@ga.attention>【注意】</>任何时候在任意一个<@ga.adGacha>【中坚寻访】</>中获得6星干员，后续在<@ga.adGacha>【中坚寻访】</>中获得6星干员的概率将恢复到<@ga.percent>2%</>。\n\n<@ga.attention>【中坚选调】</>在本期<@ga.adGacha>【中坚寻访】</>中，累计寻访<@ga.attention>150</>次后，则下次招募到的六星干员必定为本期出率上升的六星干员之一（仅限一次）。累计寻访<@ga.attention>300</>次后，则下次招募到的六星干员必定为本期出率上升的另一名六星干员（仅限一次）。\n<@ga.attention>【注意】</>该累计次数会在本期<@ga.adGacha>【中坚寻访】</>的结束时清零。",
                },
                {
                    "gachaObject": "TEXT",
                    "type": 0,
                    "imageType": 0,
                    "param": "【通用凭证】获取规则",
                },
                {"gachaObject": "IMAGE", "type": 0, "imageType": 0, "param": null},
            ]

        else:
            gacha_obj_list.append(
                {
                    "gachaObject": "TEXT",
                    "type": 5,
                    "imageType": 0,
                    "param": "在所有<@ga.adGacha>【标准寻访】</>中，如果连续<@ga.percent>50</>次没有获得6星干员，则下一次获得6星干员的概率将从原本的<@ga.percent>2%</>提升至<@ga.percent>4%</>。如果该次还没有寻访到6星干员，则下一次寻访获得6星的概率由<@ga.percent>4%</>提升到<@ga.percent>6%</>。依此类推，每次提高<@ga.percent>2%</>获得6星干员的概率，直至达到<@ga.percent>100%</>时必定获得6星干员。\n在任何一个<@ga.adGacha>【标准寻访】</>中，没有获得6星干员时，都会累积次数，该次数不会因为<@ga.adGacha>【标准寻访】</>的结束而清零。因为累积次数而增加的获得概率，也会应用于接下来任意一次<@ga.adGacha>【标准寻访】</>。\n<@ga.attention>【注意】</>任何时候在任意一个<@ga.adGacha>【标准寻访】</>中获得6星干员，后续在<@ga.adGacha>【标准寻访】</>中获得6星干员的概率将恢复到<@ga.percent>2%</>。\n\n<@ga.attention>【标准选调】</>在本期<@ga.adGacha>【标准寻访】</>中，累计寻访<@ga.attention>150</>次后，则下次招募到的六星干员必定为本期出率上升的六星干员之一（仅限一次）。累计寻访<@ga.attention>300</>次后，则下次招募到的六星干员必定为本期出率上升的另一名六星干员（仅限一次）。\n<@ga.attention>【注意】</>该累计次数会在本期<@ga.adGacha>【标准寻访】</>的结束时清零。",
                }
            )

        self.response["detailInfo"]["gachaObjList"] = gacha_obj_list


class AdvancedGachaSingleManager(AdvancedGachaSimpleManager):
    def __init__(self, player_data, request_json, response, pool_id, gacha_type):
        super().__init__(player_data, request_json, response, pool_id, gacha_type)

        up_char_info = self.get_up_char_info()

        self.is_valid_pool = True
        if (
            CharRarityRank.TIER_6.name not in up_char_info
            or len(up_char_info[CharRarityRank.TIER_6.name]["char_id_lst"]) != 1
        ):
            self.is_valid_pool = False

        if not self.is_valid_pool:
            print(f"warn: single pool {self.pool_id} misconfigured")

        if self.is_valid_pool:
            self.single_char_id = up_char_info[CharRarityRank.TIER_6.name][
                "char_id_lst"
            ][0]

    def get_single_pity_key(self):
        return f"advanced_gacha_single_pity_{self.pool_id}"

    def get_single_pity(self):
        single_pity_key = self.get_single_pity_key()

        return self.player_data.extra_save.save_obj.get(single_pity_key, 0)

    def set_single_pity(self, single_pity):
        single_pity_key = self.get_single_pity_key()

        self.player_data.extra_save.save_obj[single_pity_key] = single_pity

    def post_gacha_override(self, char_rarity_rank, char_id):
        char_rarity_rank, char_id = super().post_gacha_override(
            char_rarity_rank, char_id
        )

        if not self.is_valid_pool:
            return char_rarity_rank, char_id

        single_pity = self.get_single_pity()
        if single_pity >= 150 and char_rarity_rank == CharRarityRank.TIER_6:
            char_id = self.single_char_id

        return char_rarity_rank, char_id

    def post_gacha_operations(self, char_rarity_rank, char_id):
        super().post_gacha_operations(char_rarity_rank, char_id)

        if not self.is_valid_pool:
            return

        if self.pool_id not in self.player_data["gacha"]["single"]:
            self.player_data["gacha"]["single"][self.pool_id] = {
                "singleEnsureCnt": 0,
                "singleEnsureUse": false,
                "singleEnsureChar": self.single_char_id,
            }

        single_pity = self.get_single_pity()
        if single_pity != -1:
            if single_pity >= 150 and char_rarity_rank == CharRarityRank.TIER_6:
                single_pity = -1
            elif char_id == self.single_char_id:
                single_pity = 0
            else:
                single_pity += 1
            self.set_single_pity(single_pity)

        if single_pity >= 150:
            single_ensure_cnt = -1
        else:
            single_ensure_cnt = single_pity

        self.player_data["gacha"]["single"][self.pool_id]["singleEnsureCnt"] = (
            single_ensure_cnt
        )
        self.player_data["gacha"]["single"][self.pool_id]["singleEnsureUse"] = (
            single_pity == -1
        )

    def gacha_getPoolDetail(self):
        super().gacha_getPoolDetail()

        gacha_obj_list = self.response["detailInfo"]["gachaObjList"]

        gacha_obj_list.append(
            {
                "gachaObject": "TEXT",
                "type": 5,
                "imageType": 0,
                "param": "在所有<@ga.adGacha>【标准寻访】</>中，如果连续<@ga.percent>50</>次没有获得6星干员，则下一次获得6星干员的概率将从原本的<@ga.percent>2%</>提升至<@ga.percent>4%</>。如果该次还没有寻访到6星干员，则下一次寻访获得6星的概率由<@ga.percent>4%</>提升到<@ga.percent>6%</>。依此类推，每次提高<@ga.percent>2%</>获得6星干员的概率，直至达到<@ga.percent>100%</>时必定获得6星干员。\n在任何一个<@ga.adGacha>【标准寻访】</>中，没有获得6星干员时，都会累积次数，该次数不会因为<@ga.adGacha>【标准寻访】</>的结束而清零。因为累积次数而增加的获得概率，也会应用于接下来任意一次<@ga.adGacha>【标准寻访】</>。\n<@ga.attention>【注意】</>任何时候在任意一个<@ga.adGacha>【标准寻访】</>中获得6星干员，后续在<@ga.adGacha>【标准寻访】</>中获得6星干员的概率将恢复到<@ga.percent>2%</>。\n\n<@ga.attention>【定向选调】</>在本期寻访中，如果连续<@ga.percent>150</>次没有获得本期出率上升的六星干员，则下一次招募到的六星干员<@ga.attention>必定为本期出率上升的六星干员</>。该机制在本期寻访中仅生效一次。\n本期寻访的<@ga.attention>【定向选调】</>累计次数会在寻访结束时清零，不会累计到后续的其他<@ga.adGacha>【标准寻访】</>中。",
            }
        )

        self.response["detailInfo"]["gachaObjList"] = gacha_obj_list


class AdvancedGachaNewbeeManager(AdvancedGachaSimpleManager):
    def get_basic_tier_6_pity(self):
        return 0

    def set_basic_tier_6_pity(self, basic_tier_6_pity):
        return

    def get_basic_tier_5_pity(self):
        return True

    def set_basic_tier_5_pity(self):
        return

    def get_boot_tier_6_pity_key(self):
        return "advanced_gacha_boot_tier_6_pity"

    def get_boot_tier_6_pity(self):
        boot_tier_6_pity_key = self.get_boot_tier_6_pity_key()

        return self.player_data.extra_save.save_obj.get(boot_tier_6_pity_key, False)

    def set_boot_tier_6_pity(self):
        boot_tier_6_pity_key = self.get_boot_tier_6_pity_key()

        self.player_data.extra_save.save_obj[boot_tier_6_pity_key] = True

    def get_boot_tier_5_pity_key(self):
        return "advanced_gacha_boot_tier_5_pity"

    def get_boot_tier_5_pity(self):
        boot_tier_5_pity_key = self.get_boot_tier_5_pity_key()

        return self.player_data.extra_save.save_obj.get(boot_tier_5_pity_key, False)

    def set_boot_tier_5_pity(self):
        boot_tier_5_pity_key = self.get_boot_tier_5_pity_key()

        self.player_data.extra_save.save_obj[boot_tier_5_pity_key] = True

    def pre_gacha_override(self):
        char_rarity_rank, char_id = super().pre_gacha_override()

        gacha_num = self.get_gacha_num()

        if gacha_num + 1 == 10:
            if not self.get_boot_tier_6_pity():
                char_rarity_rank = CharRarityRank.TIER_6
        elif gacha_num + 1 == 20:
            if not self.get_boot_tier_5_pity():
                char_rarity_rank = CharRarityRank.TIER_5

        return char_rarity_rank, char_id

    def post_gacha_operations(self, char_rarity_rank, char_id):
        super().post_gacha_operations(char_rarity_rank, char_id)

        cnt = self.player_data["gacha"]["newbee"]["cnt"] - 1
        self.player_data["gacha"]["newbee"]["cnt"] = cnt

        self.player_data["gacha"]["newbee"]["openFlag"] = int(cnt != 0)

        if char_rarity_rank == CharRarityRank.TIER_6:
            if not self.get_boot_tier_6_pity():
                self.set_boot_tier_6_pity()
            else:
                self.set_boot_tier_5_pity()
        elif char_rarity_rank == CharRarityRank.TIER_5:
            self.set_boot_tier_5_pity()

    def get_avail_char_info(self):
        gacha_data = const_json_loader[GACHA_DATA]
        return gacha_data["newbee_avail_char_info"]

    def gacha_getPoolDetail(self):
        super().gacha_getPoolDetail()

        self.response["detailInfo"]["gachaObjList"] = [
            {"gachaObject": "TEXT", "type": 3, "imageType": 0, "param": "卡池干员列表"},
            {
                "gachaObject": "TEXT",
                "type": 4,
                "imageType": 0,
                "param": "只包含为新人特别挑选的干员",
            },
            {
                "gachaObject": "TEXT",
                "type": 1,
                "imageType": 0,
                "param": "全部可能出现的干员",
            },
            {"gachaObject": "AVAIL_CHAR", "type": 0, "imageType": 0, "param": null},
            {
                "gachaObject": "TEXT",
                "type": 3,
                "imageType": 0,
                "param": "该寻访为【新人特惠寻访】",
            },
            {
                "gachaObject": "TEXT",
                "type": 5,
                "imageType": 0,
                "param": "<@ga.nbGacha>【新人特惠寻访】</>中，每次寻访的价格低于<@ga.adGacha>【标准寻访】</>，能够获得的干员为特别指定，如上所列。",
            },
        ]


def get_advanced_gacha_manager(player_data, request_json, response):
    pool_id = request_json["poolId"]
    gacha_type = pool_id_gacha_type_dict[pool_id]
    if gacha_type == "double":
        return AdvancedGachaDoubleManager(
            player_data, request_json, response, pool_id, gacha_type
        )
    if gacha_type == "single":
        return AdvancedGachaSingleManager(
            player_data, request_json, response, pool_id, gacha_type
        )
    if gacha_type == "newbee":
        return AdvancedGachaNewbeeManager(
            player_data, request_json, response, pool_id, gacha_type
        )
    return AdvancedGachaSimpleManager(
        player_data, request_json, response, pool_id, gacha_type
    )


@bp_gacha.route("/gacha/advancedGacha", methods=["POST"])
@player_data_decorator
def gacha_advancedGacha(player_data):
    request_json = request.get_json()
    response = {}

    advanced_gacha_manager = get_advanced_gacha_manager(
        player_data, request_json, response
    )
    advanced_gacha_manager.gacha_advancedGacha()

    return response


@bp_gacha.route("/gacha/tenAdvancedGacha", methods=["POST"])
@player_data_decorator
def gacha_tenAdvancedGacha(player_data):
    request_json = request.get_json()
    response = {}

    advanced_gacha_manager = get_advanced_gacha_manager(
        player_data, request_json, response
    )
    advanced_gacha_manager.gacha_tenAdvancedGacha()

    return response


@bp_gacha.route("/gacha/getPoolDetail", methods=["POST"])
@player_data_decorator
def gacha_getPoolDetail(player_data):
    request_json = request.get_json()
    response = {}

    advanced_gacha_manager = get_advanced_gacha_manager(
        player_data, request_json, response
    )
    advanced_gacha_manager.gacha_getPoolDetail()

    return response


@bp_gacha.route("/gacha/choosePoolUp", methods=["POST"])
@player_data_decorator
def gacha_choosePoolUp(player_data):
    request_json = request.get_json()
    response = {}

    advanced_gacha_manager = get_advanced_gacha_manager(
        player_data, request_json, response
    )
    advanced_gacha_manager.gacha_choosePoolUp()

    return response
