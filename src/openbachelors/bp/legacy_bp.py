from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.helper import get_char_id_from_skin_id

router = APIRouter()


@router.post("/user/changeSecretary")
@player_data_decorator
async def user_changeSecretary(player_data, request: Request):
    request_json = await request.json()

    skin_id = request_json["skinId"]
    # broken (by amiya)
    char_id = get_char_id_from_skin_id(skin_id)

    player_data["status"] = {
        "secretary": char_id,
        "secretarySkinId": skin_id,
    }

    response = {}
    return response


@router.post("/background/setBackground")
@player_data_decorator
async def background_setBackground(player_data, request: Request):
    request_json = await request.json()

    player_data["background"]["selected"] = request_json["bgID"]

    response = {}
    return response


@router.post("/homeTheme/change")
@player_data_decorator
async def homeTheme_change(player_data, request: Request):
    request_json = await request.json()

    player_data["homeTheme"]["selected"] = request_json["themeId"]

    response = {}
    return response
