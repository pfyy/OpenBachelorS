from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, CRISIS_V2_TABLE
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.battle_log_logger import log_battle_log_if_necessary


router = APIRouter()


@router.post("/recalRune/battleStart")
@player_data_decorator
async def recalRune_battleStart(player_data, request: Request):
    request_json = await request.json()

    player_data.extra_save.save_obj["recalRune_seasonId"] = request_json["seasonId"]
    player_data.extra_save.save_obj["recalRune_stageId"] = request_json["stageId"]
    player_data.extra_save.save_obj["recalRune_runes"] = request_json["runes"]

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


def get_rune_score(season_id, stage_id, rune_lst):
    crisis_v2_table = const_json_loader[CRISIS_V2_TABLE]

    rune_score = 0

    for rune_id in rune_lst:
        rune_score += crisis_v2_table["recalRuneData"]["seasons"][season_id]["stages"][
            stage_id
        ]["runes"][rune_id]["score"]

    return rune_score


@router.post("/recalRune/battleFinish")
@player_data_decorator
async def recalRune_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    season_id = player_data.extra_save.save_obj["recalRune_seasonId"]
    stage_id = player_data.extra_save.save_obj["recalRune_stageId"]

    rune_lst = player_data.extra_save.save_obj["recalRune_runes"]

    rune_score = get_rune_score(season_id, stage_id, rune_lst)

    response = {
        "seasonId": season_id,
        "stageId": stage_id,
        "state": 1,
        "score": rune_score,
        "newRecord": false,
        "runes": rune_lst,
        "hp": 3,
        "ts": 1700000000,
    }
    return response
