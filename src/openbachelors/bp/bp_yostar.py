from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

router = APIRouter()


@router.post("/yostar/get-auth")
async def yostar_get_auth(request: Request):
    request_json = await request.json()

    response = {
        "Code": 200,
        "Data": {
            "UID": "123456789",
            "Token": request_json["Account"],
            "Account": "123456789",
        },
        "Msg": "OK",
    }
    return response
