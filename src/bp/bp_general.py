from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.faketime import faketime


bp_general = Blueprint("bp_general", __name__)


@bp_general.route("/general/v1/server_time")
def general_v1_server_time():
    t = int(faketime())
    response = {
        "data": {"serverTime": t, "isHoliday": false},
        "msg": "OK",
        "status": 0,
        "type": "A",
    }
    return response


@bp_general.route("/general/v1/send_phone_code", methods=["POST"])
def general_v1_send_phone_code():
    response = {"msg": "OK", "status": 0, "type": "A"}
    return response
