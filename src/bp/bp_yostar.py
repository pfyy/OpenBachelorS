from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

bp_yostar = Blueprint("bp_yostar", __name__)


@bp_yostar.route("/yostar/get-auth", methods=["POST"])
def yostar_get_auth():
    request_json = request.get_json()

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
