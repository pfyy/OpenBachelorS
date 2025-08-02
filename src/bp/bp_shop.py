from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

bp_shop = Blueprint("bp_shop", __name__)


@bp_shop.route("/shop/getSkinGoodList", methods=["POST"])
@player_data_decorator
def shop_getSkinGoodList(player_data):
    request_json = request.get_json()
    response = {"goodList": []}
    return response


@bp_shop.route("/shop/getFurniGoodList", methods=["POST"])
@player_data_decorator
def shop_getFurniGoodList(player_data):
    request_json = request.get_json()
    response = {"goods": [], "groups": []}
    return response


@bp_shop.route("/shop/getSocialGoodList", methods=["POST"])
@player_data_decorator
def shop_getSocialGoodList(player_data):
    request_json = request.get_json()
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


@bp_shop.route("/shop/getLowGoodList", methods=["POST"])
@player_data_decorator
def shop_getLowGoodList(player_data):
    request_json = request.get_json()
    response = {
        "groups": [],
        "goodList": [],
        "shopEndTime": 2147483647,
        "newFlag": [],
    }
    return response


@bp_shop.route("/shop/getHighGoodList", methods=["POST"])
@player_data_decorator
def shop_getHighGoodList(player_data):
    request_json = request.get_json()
    response = {
        "goodList": [],
        "progressGoodList": {},
        "newFlag": [],
    }
    return response


@bp_shop.route("/shop/getClassicGoodList", methods=["POST"])
@player_data_decorator
def shop_getClassicGoodList(player_data):
    request_json = request.get_json()
    response = {
        "goodList": [],
        "progressGoodList": {},
        "newFlag": [],
    }
    return response


@bp_shop.route("/shop/getExtraGoodList", methods=["POST"])
@player_data_decorator
def shop_getExtraGoodList(player_data):
    request_json = request.get_json()
    response = {
        "goodList": [],
        "newFlag": [],
        "lastClick": 1700000000,
    }
    return response


@bp_shop.route("/shop/getEPGSGoodList", methods=["POST"])
@player_data_decorator
def shop_getEPGSGoodList(player_data):
    request_json = request.get_json()
    response = {
        "goodList": [],
    }
    return response


@bp_shop.route("/shop/getRepGoodList", methods=["POST"])
@player_data_decorator
def shop_getRepGoodList(player_data):
    request_json = request.get_json()
    response = {
        "goodList": [],
        "newFlag": [],
    }
    return response


@bp_shop.route("/shop/getCashGoodList", methods=["POST"])
@player_data_decorator
def shop_getCashGoodList(player_data):
    request_json = request.get_json()
    response = {
        "goodList": [],
    }
    return response


@bp_shop.route("/shop/getGPGoodList", methods=["POST"])
@player_data_decorator
def shop_getGPGoodList(player_data):
    request_json = request.get_json()
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


@bp_shop.route("/shop/getGoodPurchaseState", methods=["POST"])
@player_data_decorator
def shop_getGoodPurchaseState(player_data):
    request_json = request.get_json()
    response = {
        "result": {},
    }
    return response


@bp_shop.route("/shop/getLMTGSGoodList", methods=["POST"])
@player_data_decorator
def shop_getLMTGSGoodList(player_data):
    request_json = request.get_json()
    response = {
        "goodList": [],
    }
    return response
