from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader


bp_user = Blueprint("bp_user", __name__)


@bp_user.route("/user/auth/v1/token_by_phone_password", methods=["POST"])
def user_auth_v1_token_by_phone_password():
    request_json = request.get_json()

    phone = request_json["phone"]

    response = {"data": {"token": phone}, "msg": "OK", "status": 0, "type": "A"}
    return response


@bp_user.route("/user/info/v1/basic")
def user_info_v1_basic():
    token = request.args.get("token")
    response = {
        "data": {
            "hgId": "123456789",
            "phone": token,
            "email": null,
            "identityNum": "123456789",
            "identityName": "123456789",
            "isMinor": false,
            "isLatestUserAgreement": true,
        },
        "msg": "OK",
        "status": 0,
        "type": "A",
    }
    return response


@bp_user.route("/user/oauth2/v2/grant", methods=["POST"])
def user_oauth2_v2_grant():
    request_json = request.get_json()

    token = request_json["token"]

    response = {
        "data": {"uid": "123456789", "code": token},
        "msg": "OK",
        "status": 0,
        "type": "A",
    }
    return response
