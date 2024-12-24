from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.helper import get_char_num_id

bp_char = Blueprint("bp_char", __name__)


@bp_char.route("/char/changeMarkStar", methods=["POST"])
@player_data_decorator
def char_changeMarkStar(player_data):
    request_json = request.get_json()

    for char_id in request_json["set"]:
        char_num_id = get_char_num_id(char_id)

        player_data["troop"]["chars"][str(char_num_id)]["starMark"] = request_json[
            "set"
        ][char_id]

    response = {}
    return response
