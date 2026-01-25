from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, ASSIST_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.helper import (
    get_char_num_id,
    get_friend_uid_from_assist_lst_idx,
    get_assist_lst_idx_from_friend_uid,
    convert_char_obj_to_assist_char_obj,
    get_friend_uid_from_assist_lst_idx_ext,
    get_assist_lst_idx_from_friend_uid_ext,
)
from ..util.battle_log_logger import log_battle_log_if_necessary
from ..util.assist_ext import profession_lst, profession_assist_lst_dict


router = APIRouter()


@router.post("/quest/squadFormation")
@player_data_decorator
async def quest_squadFormation(player_data, request: Request):
    request_json = await request.json()

    squad_id = request_json["squadId"]
    player_data["troop"]["squads"][squad_id]["slots"] = request_json["slots"]

    response = {}
    return response


@router.post("/quest/changeSquadName")
@player_data_decorator
async def quest_changeSquadName(player_data, request: Request):
    request_json = await request.json()

    squad_id = request_json["squadId"]
    player_data["troop"]["squads"][squad_id]["name"] = request_json["name"]

    response = {}
    return response


@router.post("/quest/battleStart")
@player_data_decorator
async def quest_battleStart(player_data, request: Request):
    request_json = await request.json()

    stage_id = request_json["stageId"]
    player_data.extra_save.save_obj["cur_stage_id"] = stage_id

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
        "apFailReturn": 0,
        "isApProtect": 0,
        "inApProtectPeriod": false,
        "notifyPowerScoreNotEnoughIfFailed": false,
    }
    return response


@router.post("/quest/battleFinish")
@player_data_decorator
async def quest_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "apFailReturn": 0,
        "expScale": 1.2,
        "goldScale": 1.2,
        "rewards": [],
        "firstRewards": [],
        "unlockStages": [],
        "unusualRewards": [],
        "additionalRewards": [],
        "furnitureRewards": [],
        "overrideRewards": [],
        "alert": [],
        "suggestFriend": false,
        "pryResult": [],
        "itemReturn": [],
        "extra": {
            "sixStar": {
                "groupId": "main_15",
                "before": 32,
                "after": 32,
                "stageBefore": 2,
            }
        },
    }
    return response


@router.post("/quest/battleContinue")
@player_data_decorator
async def quest_battleContinue(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 1,
        "battleId": "00000000-0000-0000-0000-000000000000",
        "apFailReturn": 0,
    }
    return response


NUM_ASSIST_PER_PAGE = 9


def get_num_assist_page(assist_lst):
    # simple math
    return (len(assist_lst) + NUM_ASSIST_PER_PAGE - 1) // NUM_ASSIST_PER_PAGE


def get_assist_page_key(request_json):
    if const_json_loader[CONFIG_JSON]["assist_ext"]:
        profession = request_json["profession"]
        return f"assist_ext_paging_{profession}"

    return "assist_default_paging"


def get_assist_page_idx(player_data, request_json):
    assist_page_key = get_assist_page_key(request_json)
    return player_data.extra_save.save_obj.get(assist_page_key, 0)


def set_assist_page_idx(player_data, request_json, assist_page_idx):
    assist_page_key = get_assist_page_key(request_json)
    player_data.extra_save.save_obj[assist_page_key] = assist_page_idx


@router.post("/quest/getAssistList")
@player_data_decorator
async def quest_getAssistList(player_data, request: Request):
    request_json = await request.json()

    if const_json_loader[CONFIG_JSON]["assist_ext"]:
        profession = request_json["profession"]
        profession_idx = profession_lst.copy().index(profession)
        assist_lst = profession_assist_lst_dict[profession].copy()
        friend_uid_lst = [
            get_friend_uid_from_assist_lst_idx_ext(i, profession_idx)
            for i in range(len(assist_lst))
        ]
    else:
        assist_lst = const_json_loader[ASSIST_JSON]["assist_lst"].copy()
        friend_uid_lst = [
            get_friend_uid_from_assist_lst_idx(i) for i in range(len(assist_lst))
        ]

    num_assist_page = get_num_assist_page(assist_lst)

    assist_page_idx = get_assist_page_idx(player_data, request_json) % num_assist_page

    if request_json["askRefresh"]:
        assist_page_idx = (assist_page_idx + 1) % num_assist_page
        set_assist_page_idx(player_data, request_json, assist_page_idx)

    lower_bound = assist_page_idx * NUM_ASSIST_PER_PAGE
    upper_bound = (assist_page_idx + 1) * NUM_ASSIST_PER_PAGE
    assist_lst = assist_lst[lower_bound:upper_bound]
    friend_uid_lst = friend_uid_lst[lower_bound:upper_bound]

    response = {"allowAskTs": 1700000000, "assistList": []}

    for assist_char_id, friend_uid in zip(assist_lst, friend_uid_lst):
        assist_char_num_id = get_char_num_id(assist_char_id)
        assist_char_obj = player_data["troop"]["chars"][str(assist_char_num_id)].copy()
        convert_char_obj_to_assist_char_obj(assist_char_obj)
        response["assistList"].append(
            {
                "uid": friend_uid,
                "aliasName": null,
                "nickName": "Undergraduate",
                "nickNumber": "1234",
                "level": 120,
                "avatarId": "0",
                "avatar": {"type": "ICON", "id": "avatar_def_01"},
                "lastOnlineTime": 1700000000,
                "assistCharList": [assist_char_obj, null, null],
                "powerScore": 0,
                "isFriend": true,
                "canRequestFriend": false,
                "assistSlotIndex": 0,
            }
        )

    return response


@router.post("/quest/saveBattleReplay")
@player_data_decorator
async def quest_saveBattleReplay(player_data, request: Request):
    request_json = await request.json()

    response = {}

    if player_data.extra_save.save_obj.get("cur_stage_id", None) is None:
        return response

    stage_id = player_data.extra_save.save_obj["cur_stage_id"]

    battle_replay = request_json["battleReplay"]

    await player_data.battle_replay_manager.save_battle_replay(stage_id, battle_replay)

    player_data["dungeon"]["stages"][stage_id]["hasBattleReplay"] = 1

    return response


@router.post("/quest/getBattleReplay")
@player_data_decorator
async def quest_getBattleReplay(player_data, request: Request):
    request_json = await request.json()

    stage_id = request_json["stageId"]

    battle_replay = await player_data.battle_replay_manager.load_battle_replay(stage_id)

    response = {"battleReplay": battle_replay}
    return response


@router.post("/quest/finishStoryStage")
@player_data_decorator
async def quest_finishStoryStage(player_data, request: Request):
    request_json = await request.json()

    response = {
        "result": 0,
        "rewards": [],
        "unlockStages": [],
        "alert": [],
    }
    return response


@router.post("/quest/editStageSixStarTag")
@player_data_decorator
async def quest_editStageSixStarTag(player_data, request: Request):
    request_json = await request.json()

    stage_id = request_json["stageId"]
    tag_lst = request_json["selected"]

    player_data["dungeon"]["sixStar"]["stages"][stage_id]["tagSelected"] = tag_lst

    response = {}
    return response
