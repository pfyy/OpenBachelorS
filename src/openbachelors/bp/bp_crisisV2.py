import os
from pathlib import Path

from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, CRISIS_V2_DATA_DIRPATH
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.battle_log_logger import log_battle_log_if_necessary

router = APIRouter()


def get_crisis_v2_data():
    crisis_v2_season = const_json_loader[VERSION_JSON]["crisis_v2_season"]

    if not crisis_v2_season:
        crisis_v2_season = ""

    if crisis_v2_season:
        crisis_v2_data_filepath = Path(
            os.path.join(CRISIS_V2_DATA_DIRPATH, f"{crisis_v2_season}.json")
        ).as_posix()

        crisis_v2_data = const_json_loader[crisis_v2_data_filepath]
    else:
        crisis_v2_data = {
            "seasonId": "",
            "mapStageDataMap": {},
            "mapDetailDataMap": {},
            "seasonConst": {},
            "achievementDataMap": {},
        }

    return crisis_v2_data


@router.post("/crisisV2/getInfo")
@player_data_decorator
async def crisisV2_getInfo(player_data, request: Request):
    request_json = await request.json()

    crisis_v2_data = get_crisis_v2_data()

    response = {
        "info": crisis_v2_data.copy(),
        "ts": 1700000000,
    }
    return response


@router.post("/crisisV2/getGoodList")
@player_data_decorator
async def crisisV2_getGoodList(player_data, request: Request):
    request_json = await request.json()

    response = {
        "permanent": [],
        "season": [],
        "progressGoodList": {},
    }
    return response


@router.post("/crisisV2/getSnapshot")
@player_data_decorator
async def crisisV2_getSnapshot(player_data, request: Request):
    request_json = await request.json()

    response = {
        "detail": {},
        "simple": {},
    }
    return response


@router.post("/crisisV2/battleStart")
@player_data_decorator
async def crisisV2_battleStart(player_data, request: Request):
    request_json = await request.json()

    player_data.extra_save.save_obj["crisis_v2_map_id"] = request_json["mapId"]
    player_data.extra_save.save_obj["crisis_v2_node_lst"] = request_json["runeSlots"]

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


def get_rune_lst(map_id, node_lst):
    crisis_v2_data = get_crisis_v2_data()

    rune_lst = []
    for node_id in node_lst:
        rune_id = crisis_v2_data["mapDetailDataMap"][map_id]["nodeDataMap"][node_id][
            "runeId"
        ]
        rune_lst.append(rune_id)

    return rune_lst


def get_basic_score_vec(map_id, rune_lst):
    crisis_v2_data = get_crisis_v2_data()

    basic_score_vec = [0, 0, 0, 0, 0, 0]

    for rune_id in rune_lst:
        rune_score = crisis_v2_data["mapDetailDataMap"][map_id]["runeDataMap"][rune_id][
            "score"
        ]
        rune_dimension = crisis_v2_data["mapDetailDataMap"][map_id]["runeDataMap"][
            rune_id
        ]["dimension"]

        basic_score_vec[rune_dimension] += rune_score

    return basic_score_vec


def get_bonus_score_vec(map_id, node_lst):
    crisis_v2_data = get_crisis_v2_data()

    class MutualExclusionGroup:
        def __init__(self):
            self.max_score_node_set = set()
            self.max_score = 0

        def add(self, node_id):
            rune_id = crisis_v2_data["mapDetailDataMap"][map_id]["nodeDataMap"][
                node_id
            ]["runeId"]
            score = crisis_v2_data["mapDetailDataMap"][map_id]["runeDataMap"][rune_id][
                "score"
            ]
            if score < self.max_score:
                return

            if score > self.max_score:
                self.max_score_node_set = set()
                self.max_score = score

            self.max_score_node_set.add(node_id)

    class NodePack:
        def __init__(self, score, dimension):
            self.node_set = set()
            self.mutual_exclusion_group_dict = {}

            self.score = score
            self.dimension = dimension

        def add(self, node_id, mutual_exclusion_group_id=None):
            if mutual_exclusion_group_id is None:
                self.node_set.add(node_id)
            else:
                if mutual_exclusion_group_id not in self.mutual_exclusion_group_dict:
                    self.mutual_exclusion_group_dict[mutual_exclusion_group_id] = (
                        MutualExclusionGroup()
                    )
                self.mutual_exclusion_group_dict[mutual_exclusion_group_id].add(node_id)

        def check_bonus_available(self, selected_node_set):
            for node_id in self.node_set:
                if node_id not in selected_node_set:
                    return False

            for mutual_exclusion_group_id in self.mutual_exclusion_group_dict:
                mutual_exclusion_group = self.mutual_exclusion_group_dict[
                    mutual_exclusion_group_id
                ]
                found = False
                for node_id in mutual_exclusion_group.max_score_node_set:
                    if node_id in selected_node_set:
                        found = True
                        break
                if not found:
                    return False

            return True

    node_pack_dict = {}

    for node_pack_id, node_pack_obj in crisis_v2_data["mapDetailDataMap"][map_id][
        "bagDataMap"
    ]:
        score = node_pack_obj["rewardScore"]
        dimension = node_pack_obj["dimension"]
        node_pack_dict[node_pack_id] = NodePack(score, dimension)

    for node_id, node_obj in crisis_v2_data["mapDetailDataMap"][map_id]["nodeDataMap"]:
        node_type = node_obj["nodeType"]
        if node_type != "NORMAL":
            continue

        node_pack_id = node_obj["slotPackId"]

        if node_pack_id:
            mutual_exclusion_group_id = node_obj["mutualExclusionGroup"]
            node_pack_dict[node_pack_id].add(node_id, mutual_exclusion_group_id)

    bonus_score_vec = [0, 0, 0, 0, 0, 0]

    selected_node_set = set(node_lst)

    for node_pack_id in node_pack_dict:
        node_pack = node_pack_dict[node_pack_id]

        if node_pack.check_bonus_available(selected_node_set):
            bonus_score_vec[node_pack.dimension] += node_pack.score

    return bonus_score_vec


def get_score_vec(map_id, node_lst, rune_lst):
    basic_score_vec = get_basic_score_vec(map_id, rune_lst)
    bonus_score_vec = get_bonus_score_vec(map_id, node_lst)

    score_vec = []

    for i, j in zip(basic_score_vec, bonus_score_vec):
        score_vec.append(i + j)

    return score_vec


@router.post("/crisisV2/battleFinish")
@player_data_decorator
async def crisisV2_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    map_id = player_data.extra_save.save_obj["crisis_v2_map_id"]
    node_lst = player_data.extra_save.save_obj["crisis_v2_node_lst"]

    rune_lst = get_rune_lst(map_id, node_lst)

    score_vec = get_score_vec(map_id, node_lst, rune_lst)

    response = {
        "result": 0,
        "mapId": map_id,
        "runeIds": rune_lst,
        "isNewRecord": false,
        "scoreRecord": score_vec,
        "scoreCurrent": score_vec,
        "runeCount": [0, len(rune_lst)],
        "commentNew": [],
        "commentOld": [],
        "ts": 1700000000,
    }
    return response
