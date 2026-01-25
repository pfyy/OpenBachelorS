from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

router = APIRouter()


@router.post("/shop/getSkinGoodList")
@player_data_decorator
async def shop_getSkinGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {"goodList": []}
    return response


@router.post("/shop/getFurniGoodList")
@player_data_decorator
async def shop_getFurniGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {"goods": [], "groups": []}
    return response


@router.post("/shop/getSocialGoodList")
@player_data_decorator
async def shop_getSocialGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {
        "goodList": [],
        "charPurchase": {
            "char_198_blackd": 6,
            "char_187_ccheal": 6,
            "char_260_durnar": 6,
        },
        "costSocialPoint": 99999999,
        "creditGroup": "creditGroup2",
    }
    return response


@router.post("/shop/getLowGoodList")
@player_data_decorator
async def shop_getLowGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {
        "groups": [],
        "goodList": [],
        "shopEndTime": 2147483647,
        "newFlag": [],
    }
    return response


@router.post("/shop/getHighGoodList")
@player_data_decorator
async def shop_getHighGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {
        "goodList": [],
        "progressGoodList": {},
        "newFlag": [],
    }
    return response


@router.post("/shop/getClassicGoodList")
@player_data_decorator
async def shop_getClassicGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {
        "goodList": [],
        "progressGoodList": {},
        "newFlag": [],
    }
    return response


@router.post("/shop/getExtraGoodList")
@player_data_decorator
async def shop_getExtraGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {
        "goodList": [],
        "newFlag": [],
        "lastClick": 1700000000,
    }
    return response


@router.post("/shop/getEPGSGoodList")
@player_data_decorator
async def shop_getEPGSGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {
        "goodList": [],
    }
    return response


@router.post("/shop/getRepGoodList")
@player_data_decorator
async def shop_getRepGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {
        "goodList": [],
        "newFlag": [],
    }
    return response


@router.post("/shop/getCashGoodList")
@player_data_decorator
async def shop_getCashGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {
        "goodList": [],
    }
    return response


@router.post("/shop/getGPGoodList")
@player_data_decorator
async def shop_getGPGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {
        "weeklyGroup": {},
        "monthlyGroup": {},
        "monthlySub": [],
        "levelGP": [],
        "oneTimeGP": [],
        "chooseGroup": [],
        "condtionTriggerGroup": [],
    }
    return response


@router.post("/shop/getGoodPurchaseState")
@player_data_decorator
async def shop_getGoodPurchaseState(player_data, request: Request):
    request_json = await request.json()
    response = {
        "result": {},
    }
    return response


@router.post("/shop/getLMTGSGoodList")
@player_data_decorator
async def shop_getLMTGSGoodList(player_data, request: Request):
    request_json = await request.json()
    response = {
        "goodList": [],
    }
    return response
