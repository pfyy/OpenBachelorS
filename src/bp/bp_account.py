from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader


bp_account = Blueprint("bp_account", __name__)


@bp_account.route("/account/login", methods=["POST"])
def account_login():
    request_json = request.get_json()
    token = request_json["token"]

    response = {
        "result": 0,
        "uid": "123456789",
        "secret": token,
        "serviceLicenseVersion": 0,
        "majorVersion": "354",
    }

    return response
