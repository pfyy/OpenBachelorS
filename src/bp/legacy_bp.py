from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.helper import get_char_id_from_skin_id

legacy_bp = Blueprint("legacy_bp", __name__)


@legacy_bp.route("/user/changeSecretary", methods=["POST"])
@player_data_decorator
def user_changeSecretary(player_data):
    request_json = request.get_json()

    skin_id = request_json["skinId"]
    char_id = get_char_id_from_skin_id(skin_id)

    player_data["status"] = {
        "secretary": char_id,
        "secretarySkinId": skin_id,
    }

    response = {}
    return response


@legacy_bp.route("/background/setBackground", methods=["POST"])
@player_data_decorator
def background_setBackground(player_data):
    request_json = request.get_json()

    player_data["background"]["selected"] = request_json["bgID"]

    response = {}
    return response


@legacy_bp.route("/homeTheme/change", methods=["POST"])
@player_data_decorator
def homeTheme_change(player_data):
    request_json = request.get_json()

    player_data["homeTheme"]["selected"] = request_json["themeId"]

    response = {}
    return response
