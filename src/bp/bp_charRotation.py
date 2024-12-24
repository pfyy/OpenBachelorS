from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

bp_charRotation = Blueprint("bp_charRotation", __name__)


@bp_charRotation.route("/charRotation/createPreset", methods=["POST"])
@player_data_decorator
def charRotation_createPreset(player_data):
    request_json = request.get_json()

    max_preset_id = 1
    for i, _ in player_data["charRotation"]["preset"]:
        i = int(i)
        max_preset_id = max(max_preset_id, i)

    max_preset_id += 1
    player_data["charRotation"]["preset"][max_preset_id] = {
        "name": "未命名界面配置",
        "background": "bg_rhodes_day",
        "homeTheme": "tm_rhodes_day",
        "profile": "char_002_amiya#1",
        "profileInst": 2,
        "slots": [{"charId": "char_002_amiya", "skinId": "char_002_amiya#1"}],
    }

    response = {}
    return response


@bp_charRotation.route("/charRotation/setCurrent", methods=["POST"])
@player_data_decorator
def charRotation_setCurrent(player_data):
    request_json = request.get_json()

    preset_id = request_json["instId"]
    player_data["charRotation"]["current"] = preset_id

    response = {}
    return response


@bp_charRotation.route("/charRotation/deletePreset", methods=["POST"])
@player_data_decorator
def charRotation_deletePreset(player_data):
    request_json = request.get_json()

    preset_id = request_json["instId"]
    del player_data["charRotation"]["preset"][preset_id]

    response = {}
    return response


@bp_charRotation.route("/charRotation/updatePreset", methods=["POST"])
@player_data_decorator
def charRotation_updatePreset(player_data):
    request_json = request.get_json()

    preset_id = request_json["instId"]
    preset = request_json["data"]

    for key in preset:
        if preset[key] is not None:
            player_data["charRotation"]["preset"][preset_id][key] = preset[key]

    response = {}
    return response
