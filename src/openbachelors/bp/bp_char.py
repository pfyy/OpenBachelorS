from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.helper import get_char_num_id

router = APIRouter()


@router.post("/char/changeMarkStar")
@player_data_decorator
async def char_changeMarkStar(player_data, request: Request):
    request_json = await request.json()

    for char_id in request_json["set"]:
        char_num_id = get_char_num_id(char_id)

        player_data["troop"]["chars"][str(char_num_id)]["starMark"] = request_json[
            "set"
        ][char_id]

    response = {}
    return response
