from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, ACTIVITY_TABLE
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.battle_log_logger import log_battle_log_if_necessary

router = APIRouter()


@router.post("/aprilFool/act6fun/battleStart")
@player_data_decorator
async def aprilFool_act6fun_battleStart(player_data, request: Request):
    request_json = await request.json()
    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/aprilFool/act6fun/battleFinish")
@player_data_decorator
async def aprilFool_act6fun_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "completeState": 2,
        "passSec": 0,
        "newRecord": false,
        "coin": 0,
    }
    return response


@router.post("/aprilFool/act5fun/battleStart")
@player_data_decorator
async def aprilFool_act5fun_battleStart(player_data, request: Request):
    request_json = await request.json()
    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/aprilFool/act5fun/battleFinish")
@player_data_decorator
async def aprilFool_act5fun_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 3,
        "score": 999999999,
        "isHighScore": false,
        "npcResult": {
            "act5fun_npc_01": 10,
            "act5fun_npc_02": 10,
            "act5fun_npc_03": 10,
            "act5fun_npc_04": 10,
            "act5fun_npc_05": 10,
        },
        "playerResult": {"totalWin": 10, "streak": 10, "totalRound": 10},
        "reward": [],
    }
    return response


@router.post("/aprilFool/act4fun/battleStart")
@player_data_decorator
async def aprilFool_act4fun_battleStart(player_data, request: Request):
    request_json = await request.json()
    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/aprilFool/act4fun/battleFinish")
@player_data_decorator
async def aprilFool_act4fun_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    activity_table = const_json_loader[ACTIVITY_TABLE]

    material_lst = []

    material_inst_id = 0

    for material_id, material_obj in activity_table["actFunData"]["act4FunData"][
        "spMatDict"
    ]:
        material_lst.append(
            {
                "instId": material_inst_id,
                "materialId": material_id,
                "materialType": 1,
            }
        )

        material_inst_id += 1

    response = {
        "materials": material_lst,
        "liveId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/aprilFool/act4fun/liveSettle")
@player_data_decorator
async def aprilFool_act4fun_liveSettle(player_data, request: Request):
    request_json = await request.json()

    response = {
        "ending": "goodending_1",
    }
    return response


@router.post("/aprilFool/act3fun/battleStart")
@player_data_decorator
async def aprilFool_act3fun_battleStart(player_data, request: Request):
    request_json = await request.json()
    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
        "apFailReturn": 0,
    }
    return response


@router.post("/aprilFool/act3fun/battleFinish")
@player_data_decorator
async def aprilFool_act3fun_battleFinish(player_data, request: Request):
    request_json = await request.json()

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
        "suggestFriend": null,
        "score": 0,
        "scoreItem": [0, 0, 0, 0, 0, 0],
        "rank": [0],
        "inRank": true,
    }
    return response
