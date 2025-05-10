from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.battle_log_logger import log_battle_log_if_necessary

misc_bp = Blueprint("misc_bp", __name__)


@misc_bp.route("/deepSea/branch", methods=["POST"])
@player_data_decorator
def deepSea_branch(player_data):
    request_json = request.get_json()

    for branch in request_json["branches"]:
        tech_tree_id = branch["techTreeId"]
        branch_id = branch["branchId"]

        player_data["deepSea"]["techTrees"][tech_tree_id]["branch"] = branch_id

    response = {}
    return response


@misc_bp.route("/act25side/battleStart", methods=["POST"])
@player_data_decorator
def act25side_battleStart(player_data):
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


@misc_bp.route("/act25side/battleFinish", methods=["POST"])
@player_data_decorator
def act25side_battleFinish(player_data):
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
    }
    return response


@misc_bp.route("/charm/setSquad", methods=["POST"])
@player_data_decorator
def charm_setSquad(player_data):
    request_json = request.get_json()

    player_data["charm"]["squad"] = request_json["squad"]

    response = {}
    return response


@misc_bp.route("/car/confirmBattleCar", methods=["POST"])
@player_data_decorator
def car_confirmBattleCar(player_data):
    request_json = request.get_json()

    player_data["car"]["battleCar"] = request_json["car"]

    response = {}
    return response


@misc_bp.route("/retro/typeAct20side/competitionStart", methods=["POST"])
@player_data_decorator
def retro_typeAct20side_competitionStart(player_data):
    request_json = request.get_json()
    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@misc_bp.route("/retro/typeAct20side/competitionFinish", methods=["POST"])
@player_data_decorator
def retro_typeAct20side_competitionFinish(player_data):
    request_json = request.get_json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "performance": 0,
        "expression": 0,
        "operation": 0,
        "total": 0,
        "level": "SS",
        "isNew": false,
    }
    return response


@misc_bp.route("/trainingGround/battleStart", methods=["POST"])
@player_data_decorator
def trainingGround_battleStart(player_data):
    request_json = request.get_json()
    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@misc_bp.route("/trainingGround/battleFinish", methods=["POST"])
@player_data_decorator
def trainingGround_battleFinish(player_data):
    request_json = request.get_json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "firstRewards": [],
    }
    return response


@misc_bp.route("/medal/setCustomData", methods=["POST"])
@player_data_decorator
def medal_setCustomData(player_data):
    request_json = request.get_json()

    custom_data = request_json["data"]

    player_data["medal"]["custom"]["customs"]["1"] = custom_data

    response = {}
    return response


@misc_bp.route("/firework/savePlateSlots", methods=["POST"])
@player_data_decorator
def firework_savePlateSlots(player_data):
    request_json = request.get_json()

    player_data["firework"]["plate"]["slots"] = request_json["slots"]

    response = {}
    return response


@misc_bp.route("/firework/changeAnimal", methods=["POST"])
@player_data_decorator
def firework_changeAnimal(player_data):
    request_json = request.get_json()

    player_data["firework"]["animal"]["select"] = request_json["animal"]

    response = {
        "animal": request_json["animal"],
    }
    return response


@misc_bp.route("/activity/enemyDuel/singleBattleStart", methods=["POST"])
@player_data_decorator
def activity_enemyDuel_singleBattleStart(player_data):
    request_json = request.get_json()

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@misc_bp.route("/activity/enemyDuel/singleBattleFinish", methods=["POST"])
@player_data_decorator
def activity_enemyDuel_singleBattleFinish(player_data):
    request_json = request.get_json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "choiceCnt": {"skip": 0, "normal": 5, "allIn": 5},
        "commentId": "Comment_Operation_1",
        "isHighScore": false,
        "rankList": [
            {"id": "1", "rank": 1, "score": 262900, "isPlayer": 1},
            {"id": "act1enemyduel_npc_01", "rank": 2, "score": 0, "isPlayer": 0},
            {"id": "act1enemyduel_npc_02", "rank": 2, "score": 0, "isPlayer": 0},
            {"id": "act1enemyduel_npc_03", "rank": 2, "score": 0, "isPlayer": 0},
            {"id": "act1enemyduel_npc_04", "rank": 2, "score": 0, "isPlayer": 0},
            {"id": "act1enemyduel_npc_05", "rank": 2, "score": 0, "isPlayer": 0},
            {"id": "act1enemyduel_npc_06", "rank": 2, "score": 0, "isPlayer": 0},
            {"id": "act1enemyduel_npc_07", "rank": 2, "score": 0, "isPlayer": 0},
        ],
        "bp": 0,
        "dailyMission": {"add": 0, "reward": 0},
    }
    return response
