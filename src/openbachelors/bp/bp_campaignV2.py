from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.battle_log_logger import log_battle_log_if_necessary

router = APIRouter()


@router.post("/campaignV2/battleStart")
@player_data_decorator
async def campaignV2_battleStart(player_data, request: Request):
    request_json = await request.json()

    stage_id = request_json["stageId"]
    player_data.extra_save.save_obj["cur_stage_id"] = stage_id

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/campaignV2/battleFinish")
@player_data_decorator
async def campaignV2_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "apFailReturn": 0,
        "rewards": [],
        "unusualRewards": [],
        "additionalRewards": [],
        "diamondMaterialRewards": [],
        "furnitureRewards": [],
        "currentFeeBefore": 1800,
        "currentFeeAfter": 1800,
        "unlockStages": [],
    }
    return response
