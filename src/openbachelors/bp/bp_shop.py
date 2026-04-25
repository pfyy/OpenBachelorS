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
        "groups": [
            "lggShdShopnumber84_Group_1",
            "lggShdShopnumber84_Group_2",
            "lggShdShopnumber84_Group_3",
        ],
        "goodList": [
            {
                "goodId": "LS_lggShdShopnumber84_1",
                "groupId": "lggShdShopnumber84_Group_1",
                "displayName": "寻访凭证",
                "originPrice": 240,
                "price": 240,
                "discount": 0,
                "slotId": 1,
                "availCount": 2,
                "item": {"id": "7003", "count": 1, "type": "TKT_GACHA"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_2",
                "groupId": "lggShdShopnumber84_Group_1",
                "displayName": "招聘许可",
                "originPrice": 8,
                "price": 8,
                "discount": 0,
                "slotId": 2,
                "availCount": 15,
                "item": {"id": "7001", "count": 1, "type": "TKT_RECRUIT"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_3",
                "groupId": "lggShdShopnumber84_Group_1",
                "displayName": "合成玉",
                "originPrice": 40,
                "price": 40,
                "discount": 0,
                "slotId": 3,
                "availCount": 6,
                "item": {"id": "4003", "count": 100, "type": "DIAMOND_SHD"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_4",
                "groupId": "lggShdShopnumber84_Group_1",
                "displayName": "中级作战记录",
                "originPrice": 10,
                "price": 10,
                "discount": 0,
                "slotId": 4,
                "availCount": 15,
                "item": {"id": "2003", "count": 4, "type": "CARD_EXP"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_5",
                "groupId": "lggShdShopnumber84_Group_1",
                "displayName": "龙门币",
                "originPrice": 10,
                "price": 10,
                "discount": 0,
                "slotId": 5,
                "availCount": 15,
                "item": {"id": "4001", "count": 4000, "type": "GOLD"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_6",
                "groupId": "lggShdShopnumber84_Group_1",
                "displayName": "赤金",
                "originPrice": 10,
                "price": 10,
                "discount": 0,
                "slotId": 6,
                "availCount": 15,
                "item": {"id": "3003", "count": 8, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_7",
                "groupId": "lggShdShopnumber84_Group_1",
                "displayName": "家具零件",
                "originPrice": 40,
                "price": 40,
                "discount": 0,
                "slotId": 7,
                "availCount": 5,
                "item": {"id": "3401", "count": 100, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_8",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "公开招募★3兑换券·I",
                "originPrice": 200,
                "price": 200,
                "discount": 0,
                "slotId": 1,
                "availCount": 1,
                "item": {
                    "id": "voucher_recruitR3_1",
                    "count": 1,
                    "type": "VOUCHER_PICK",
                },
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_9",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "公开招募★4兑换券·I",
                "originPrice": 750,
                "price": 750,
                "discount": 0,
                "slotId": 2,
                "availCount": 1,
                "item": {
                    "id": "voucher_recruitR4_1",
                    "count": 1,
                    "type": "VOUCHER_PICK",
                },
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_10",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "寻访凭证",
                "originPrice": 450,
                "price": 450,
                "discount": 0,
                "slotId": 3,
                "availCount": 2,
                "item": {"id": "7003", "count": 1, "type": "TKT_GACHA"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_11",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "招聘许可",
                "originPrice": 15,
                "price": 15,
                "discount": 0,
                "slotId": 4,
                "availCount": 20,
                "item": {"id": "7001", "count": 1, "type": "TKT_RECRUIT"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_12",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "固源岩组",
                "originPrice": 25,
                "price": 25,
                "discount": 0,
                "slotId": 5,
                "availCount": 15,
                "item": {"id": "30013", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_13",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "糖组",
                "originPrice": 30,
                "price": 30,
                "discount": 0,
                "slotId": 6,
                "availCount": 15,
                "item": {"id": "30023", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_14",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "聚酸酯组",
                "originPrice": 30,
                "price": 30,
                "discount": 0,
                "slotId": 7,
                "availCount": 15,
                "item": {"id": "30033", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_15",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "异铁组",
                "originPrice": 35,
                "price": 35,
                "discount": 0,
                "slotId": 8,
                "availCount": 15,
                "item": {"id": "30043", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_16",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "酮凝集组",
                "originPrice": 35,
                "price": 35,
                "discount": 0,
                "slotId": 9,
                "availCount": 15,
                "item": {"id": "30053", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_17",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "全新装置",
                "originPrice": 45,
                "price": 45,
                "discount": 0,
                "slotId": 10,
                "availCount": 10,
                "item": {"id": "30063", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_18",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "扭转醇",
                "originPrice": 30,
                "price": 30,
                "discount": 0,
                "slotId": 11,
                "availCount": 15,
                "item": {"id": "30073", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_19",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "轻锰矿",
                "originPrice": 35,
                "price": 35,
                "discount": 0,
                "slotId": 12,
                "availCount": 15,
                "item": {"id": "30083", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_20",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "研磨石",
                "originPrice": 40,
                "price": 40,
                "discount": 0,
                "slotId": 13,
                "availCount": 15,
                "item": {"id": "30093", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_21",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "RMA70-12",
                "originPrice": 45,
                "price": 45,
                "discount": 0,
                "slotId": 14,
                "availCount": 10,
                "item": {"id": "30103", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_22",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "凝胶",
                "originPrice": 40,
                "price": 40,
                "discount": 0,
                "slotId": 15,
                "availCount": 10,
                "item": {"id": "31013", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_23",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "炽合金",
                "originPrice": 35,
                "price": 35,
                "discount": 0,
                "slotId": 16,
                "availCount": 10,
                "item": {"id": "31023", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_24",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "晶体元件",
                "originPrice": 30,
                "price": 30,
                "discount": 0,
                "slotId": 17,
                "availCount": 10,
                "item": {"id": "31033", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_25",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "半自然溶剂",
                "originPrice": 40,
                "price": 40,
                "discount": 0,
                "slotId": 18,
                "availCount": 10,
                "item": {"id": "31043", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_26",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "化合切削液",
                "originPrice": 40,
                "price": 40,
                "discount": 0,
                "slotId": 19,
                "availCount": 10,
                "item": {"id": "31053", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_27",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "转质盐组",
                "originPrice": 45,
                "price": 45,
                "discount": 0,
                "slotId": 20,
                "availCount": 10,
                "item": {"id": "31063", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_28",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "褐素纤维",
                "originPrice": 40,
                "price": 40,
                "discount": 0,
                "slotId": 21,
                "availCount": 10,
                "item": {"id": "31073", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_29",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "环烃聚质",
                "originPrice": 45,
                "price": 45,
                "discount": 0,
                "slotId": 22,
                "availCount": 10,
                "item": {"id": "31083", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_30",
                "groupId": "lggShdShopnumber84_Group_2",
                "displayName": "类凝结核",
                "originPrice": 40,
                "price": 40,
                "discount": 0,
                "slotId": 23,
                "availCount": 10,
                "item": {"id": "31093", "count": 1, "type": "MATERIAL"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_31",
                "groupId": "lggShdShopnumber84_Group_3",
                "displayName": "龙门币",
                "originPrice": 100,
                "price": 100,
                "discount": 0,
                "slotId": 1,
                "availCount": 15,
                "item": {"id": "4001", "count": 10000, "type": "GOLD"},
                "disableMax": false,
            },
            {
                "goodId": "LS_lggShdShopnumber84_32",
                "groupId": "lggShdShopnumber84_Group_3",
                "displayName": "合成玉",
                "originPrice": 50,
                "price": 50,
                "discount": 0,
                "slotId": 2,
                "availCount": -1,
                "item": {"id": "4003", "count": 30, "type": "DIAMOND_SHD"},
                "disableMax": false,
            },
        ],
        "shopEndTime": 2147483647,
        "newFlag": [],
        "groupsInfo": [
            {"groupId": "lggShdShopnumber84_Group_1", "lggThreshold": 0},
            {"groupId": "lggShdShopnumber84_Group_2", "lggThreshold": 1490},
            {"groupId": "lggShdShopnumber84_Group_3", "lggThreshold": 11990},
        ],
        "type": 0,
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
