from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, ACTIVITY_TABLE
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


@misc_bp.route("/activity/vecBreakV2/battleStart", methods=["POST"])
@player_data_decorator
def activity_vecBreakV2_battleStart(player_data):
    request_json = request.get_json()

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@misc_bp.route("/activity/vecBreakV2/battleFinish", methods=["POST"])
@player_data_decorator
def activity_vecBreakV2_battleFinish(player_data):
    request_json = request.get_json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "msBefore": 0,
        "msAfter": 0,
        "unlockStages": [],
        "suggestFriend": false,
        "finTs": 1700000000,
    }
    return response


@misc_bp.route("/vecBreakV2/getSeasonRecord", methods=["POST"])
@player_data_decorator
def vecBreakV2_getSeasonRecord(player_data):
    request_json = request.get_json()

    response = {
        "seasons": {},
    }
    return response


def get_vec_break_v2_defense_buff_id(activity_id, stage_id):
    activity_table = const_json_loader[ACTIVITY_TABLE]

    defense_buff_id = activity_table["activity"]["VEC_BREAK_V2"][activity_id][
        "defenseDetailDict"
    ][stage_id]["buffId"]

    return defense_buff_id


@misc_bp.route("/activity/vecBreakV2/defendBattleStart", methods=["POST"])
@player_data_decorator
def activity_vecBreakV2_defendBattleStart(player_data):
    request_json = request.get_json()

    activity_id = request_json["activityId"]
    stage_id = request_json["stageId"]

    defense_buff_id = get_vec_break_v2_defense_buff_id(activity_id, stage_id)

    defense_buff_id_lst = player_data["activity"]["VEC_BREAK_V2"][activity_id][
        "activatedBuff"
    ].copy()
    if defense_buff_id not in defense_buff_id_lst:
        defense_buff_id_lst.append(defense_buff_id)
    player_data["activity"]["VEC_BREAK_V2"][activity_id]["activatedBuff"] = (
        defense_buff_id_lst
    )

    player_data["activity"]["VEC_BREAK_V2"][activity_id]["defendStages"][stage_id][
        "defendSquad"
    ] = [{"charInstId": i["charInstId"]} for i in request_json["squad"]["slots"]]

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@misc_bp.route("/activity/vecBreakV2/defendBattleFinish", methods=["POST"])
@player_data_decorator
def activity_vecBreakV2_defendBattleFinish(player_data):
    request_json = request.get_json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "msBefore": 0,
        "msAfter": 0,
        "finTs": 1700000000,
    }
    return response


@misc_bp.route("/activity/vecBreakV2/setDefend", methods=["POST"])
@player_data_decorator
def activity_vecBreakV2_setDefend(player_data):
    request_json = request.get_json()

    activity_id = request_json["activityId"]
    stage_id = request_json["stageId"]

    defense_buff_id = get_vec_break_v2_defense_buff_id(activity_id, stage_id)

    defense_buff_id_lst = player_data["activity"]["VEC_BREAK_V2"][activity_id][
        "activatedBuff"
    ].copy()
    if defense_buff_id in defense_buff_id_lst:
        defense_buff_id_lst.remove(defense_buff_id)
    player_data["activity"]["VEC_BREAK_V2"][activity_id]["activatedBuff"] = (
        defense_buff_id_lst
    )

    player_data["activity"]["VEC_BREAK_V2"][activity_id]["defendStages"][stage_id][
        "defendSquad"
    ] = []

    response = {}
    return response


@misc_bp.route("/activity/vecBreakV2/changeBuffList", methods=["POST"])
@player_data_decorator
def activity_vecBreakV2_changeBuffList(player_data):
    request_json = request.get_json()

    activity_id = request_json["activityId"]

    player_data["activity"]["VEC_BREAK_V2"][activity_id]["activatedBuff"] = (
        request_json["buffList"]
    )

    response = {}
    return response


@misc_bp.route("/activity/bossRush/battleStart", methods=["POST"])
@player_data_decorator
def activity_bossRush_battleStart(player_data):
    request_json = request.get_json()

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
        "apFailReturn": 0,
        "isApProtect": 0,
        "inApProtectPeriod": false,
        "notifyPowerScoreNotEnoughIfFailed": false,
    }
    return response


@misc_bp.route("/activity/bossRush/battleFinish", methods=["POST"])
@player_data_decorator
def activity_bossRush_battleFinish(player_data):
    request_json = request.get_json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "apFailReturn": 0,
        "expScale": 0,
        "goldScale": 0,
        "rewards": [],
        "firstRewards": [],
        "unlockStages": [],
        "unusualRewards": [],
        "additionalRewards": [],
        "furnitureRewards": [],
        "alert": [],
        "suggestFriend": false,
        "pryResult": [],
        "wave": 3,
        "milestoneBefore": 0,
        "milestoneAdd": 0,
        "isMileStoneMax": true,
        "tokenAdd": 0,
        "isTokenMax": true,
    }
    return response


@misc_bp.route("/activity/bossRush/relicSelect", methods=["POST"])
@player_data_decorator
def activity_bossRush_relicSelect(player_data):
    request_json = request.get_json()

    player_data["activity"]["BOSS_RUSH"][request_json["activityId"]]["relic"][
        "select"
    ] = request_json["relicId"]

    response = {}
    return response
