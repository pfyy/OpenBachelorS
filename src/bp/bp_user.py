from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.helper import get_username_by_token
from ..util.player_data import player_data_decorator


bp_user = Blueprint("bp_user", __name__)


@bp_user.route("/user/auth/v1/token_by_phone_password", methods=["POST"])
@bp_user.route("/user/auth/v2/token_by_phone_code", methods=["POST"])
def user_auth_v1_token_by_phone_password():
    request_json = request.get_json()

    phone = request_json["phone"]

    response = {"data": {"token": phone}, "msg": "OK", "status": 0, "type": "A"}
    return response


@bp_user.route("/user/info/v1/basic")
def user_info_v1_basic():
    token = request.args.get("token", "")
    username = get_username_by_token(token)
    response = {
        "data": {
            "hgId": "123456789",
            "phone": username,
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


@bp_user.route("/user/online/v1/loginout", methods=["POST"])
def user_online_v1_loginout():
    request_json = request.get_json()

    response = {"msg": "OK", "status": 0, "type": "A"}
    return response


@bp_user.route("/user/info/v1/logout", methods=["POST"])
def user_info_v1_logout():
    request_json = request.get_json()

    response = {"msg": "OK", "status": 0, "type": "A"}
    return response


@bp_user.route("/user/info/v1/update_agreement", methods=["POST"])
def user_info_v1_update_agreement():
    request_json = request.get_json()

    response = {"msg": "OK", "status": 0, "type": "A"}
    return response


@bp_user.route("/user/changeAvatar", methods=["POST"])
@player_data_decorator
def user_changeAvatar(player_data):
    request_json = request.get_json()

    avatar = request_json

    player_data["status"]["avatar"] = avatar

    response = {}
    return response


@bp_user.route("/user/changeResume", methods=["POST"])
@player_data_decorator
def user_changeResume(player_data):
    request_json = request.get_json()

    resume = request_json["resume"]

    player_data["status"]["resume"] = resume

    response = {}
    return response


@bp_user.route("/user/useRenameCard", methods=["POST"])
@player_data_decorator
def user_useRenameCard(player_data):
    request_json = request.get_json()

    player_data["status"]["nickName"] = request_json["nickName"]

    response = {
        "result": 0,
    }
    return response
