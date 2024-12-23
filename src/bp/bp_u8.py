import json

from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader


bp_u8 = Blueprint("bp_u8", __name__)


@bp_u8.route("/u8/user/v1/getToken", methods=["POST"])
def u8_user_v1_getToken():
    request_json = request.get_json()
    code = json.loads(request_json["extension"])["code"]

    response = {
        "result": 0,
        "captcha": {},
        "error": "",
        "uid": "123456789",
        "channelUid": "123456789",
        "token": code,
        "isGuest": 0,
        "extension": '{"isAuthenticate":true,"isMinor":false}',
    }
    return response


@bp_u8.route("/u8/pay/getAllProductList", methods=["POST"])
def u8_pay_getAllProductList():
    response = {"productList": []}
    return response
