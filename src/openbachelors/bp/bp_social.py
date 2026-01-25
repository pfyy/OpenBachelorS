from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

router = APIRouter()


@router.post("/social/getSortListInfo")
@player_data_decorator
async def social_getSortListInfo(player_data, request: Request):
    request_json = await request.json()
    response = {"result": []}
    return response


@router.post("/social/getFriendList")
@player_data_decorator
async def social_getFriendList(player_data, request: Request):
    request_json = await request.json()
    response = {"friends": [], "friendAlias": [], "resultIdList": []}
    return response


@router.post("/social/setAssistCharList")
@player_data_decorator
async def social_setAssistCharList(player_data, request: Request):
    request_json = await request.json()

    assist_char_list = request_json["assistCharList"]

    player_data["social"]["assistCharList"] = assist_char_list

    response = {}
    return response


@router.post("/social/setCardShowMedal")
@player_data_decorator
async def social_setCardShowMedal(player_data, request: Request):
    request_json = await request.json()

    player_data["social"]["medalBoard"]["type"] = request_json["type"]
    player_data["social"]["medalBoard"]["custom"] = request_json["customIndex"]
    player_data["social"]["medalBoard"]["template"] = request_json["templateGroup"]

    response = {}
    return response


@router.post("/social/setStarFriendList")
@player_data_decorator
async def social_setStarFriendList(player_data, request: Request):
    request_json = await request.json()

    response = {
        "result": 0,
        "newIdList": [],
    }
    return response
