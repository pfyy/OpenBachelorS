from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.faketime import faketime


router = APIRouter()


@router.get("/general/v1/server_time")
async def general_v1_server_time(request: Request):
    t = int(faketime())
    response = {
        "data": {"serverTime": t, "isHoliday": false},
        "msg": "OK",
        "status": 0,
        "type": "A",
    }
    return response


@router.post("/general/v1/send_phone_code")
async def general_v1_send_phone_code(request: Request):
    response = {"msg": "OK", "status": 0, "type": "A"}
    return response
