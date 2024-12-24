from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

bp_settings = Blueprint("bp_settings", __name__)


@bp_settings.route("/setting/perf/setLowPower", methods=["POST"])
@player_data_decorator
def setting_perf_setLowPower(player_data):
    request_json = request.get_json()

    player_data["setting"]["perf"]["lowPower"] = request_json["newValue"]

    response = {}
    return response
