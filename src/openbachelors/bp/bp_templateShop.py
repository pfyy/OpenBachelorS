from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

router = APIRouter()


@router.post("/templateShop/getGoodList")
@player_data_decorator
async def templateShop_getGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {
        "data": {
            "shopId": "fake_shop",
            "type": "SHOP_RARITY_GROUP",
        },
        "nextSyncTime": -1,
    }
    return response
