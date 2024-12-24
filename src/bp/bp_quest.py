from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

bp_quest = Blueprint("bp_quest", __name__)


@bp_quest.route("/quest/squadFormation", methods=["POST"])
@player_data_decorator
def quest_squadFormation(player_data):
    request_json = request.get_json()

    squad_id = request_json["squadId"]
    player_data["troop"]["squads"][squad_id]["slots"] = request_json["slots"]

    response = {}
    return response
