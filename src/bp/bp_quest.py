from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, ASSIST_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.helper import (
    get_char_num_id,
    get_friend_uid_from_assist_lst_idx,
    get_assist_lst_idx_from_friend_uid,
    convert_char_obj_to_assist_char_obj,
)
from ..util.battle_log_logger import log_battle_log_if_necessary


bp_quest = Blueprint("bp_quest", __name__)


@bp_quest.route("/quest/squadFormation", methods=["POST"])
@player_data_decorator
def quest_squadFormation(player_data):
    request_json = request.get_json()

    squad_id = request_json["squadId"]
    player_data["troop"]["squads"][squad_id]["slots"] = request_json["slots"]

    response = {}
    return response


@bp_quest.route("/quest/changeSquadName", methods=["POST"])
@player_data_decorator
def quest_changeSquadName(player_data):
    request_json = request.get_json()

    squad_id = request_json["squadId"]
    player_data["troop"]["squads"][squad_id]["name"] = request_json["name"]

    response = {}
    return response


@bp_quest.route("/quest/battleStart", methods=["POST"])
@player_data_decorator
def quest_battleStart(player_data):
    request_json = request.get_json()

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


@bp_quest.route("/quest/battleFinish", methods=["POST"])
@player_data_decorator
def quest_battleFinish(player_data):
    request_json = request.get_json()

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


@bp_quest.route("/quest/battleContinue", methods=["POST"])
@player_data_decorator
def quest_battleContinue(player_data):
    request_json = request.get_json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 1,
        "battleId": "00000000-0000-0000-0000-000000000000",
        "apFailReturn": 0,
    }
    return response


@bp_quest.route("/quest/getAssistList", methods=["POST"])
@player_data_decorator
def quest_getAssistList(player_data):
    request_json = request.get_json()

    assist_lst = const_json_loader[ASSIST_JSON]["assist_lst"].copy()

    friend_uid_lst = [
        get_friend_uid_from_assist_lst_idx(i) for i in range(len(assist_lst))
    ]

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


@bp_quest.route("/quest/saveBattleReplay", methods=["POST"])
@player_data_decorator
def quest_saveBattleReplay(player_data):
    request_json = request.get_json()

    response = {}

    if player_data.extra_save.save_obj.get("cur_stage_id", None) is None:
        return response

    stage_id = player_data.extra_save.save_obj["cur_stage_id"]

    battle_replay = request_json["battleReplay"]

    player_data.battle_replay_manager.save_battle_replay(stage_id, battle_replay)

    player_data["dungeon"]["stages"][stage_id]["hasBattleReplay"] = 1

    return response


@bp_quest.route("/quest/getBattleReplay", methods=["POST"])
@player_data_decorator
def quest_getBattleReplay(player_data):
    request_json = request.get_json()

    stage_id = request_json["stageId"]

    battle_replay = player_data.battle_replay_manager.load_battle_replay(stage_id)

    response = {"battleReplay": battle_replay}
    return response


@bp_quest.route("/quest/finishStoryStage", methods=["POST"])
@player_data_decorator
def quest_finishStoryStage(player_data):
    request_json = request.get_json()

    response = {
        "result": 0,
        "rewards": [],
        "unlockStages": [],
        "alert": [],
    }
    return response


@bp_quest.route("/quest/editStageSixStarTag", methods=["POST"])
@player_data_decorator
def quest_editStageSixStarTag(player_data):
    request_json = request.get_json()

    stage_id = request_json["stageId"]
    tag_lst = request_json["selected"]

    player_data["dungeon"]["sixStar"]["stages"][stage_id]["tagSelected"] = tag_lst

    response = {}
    return response
