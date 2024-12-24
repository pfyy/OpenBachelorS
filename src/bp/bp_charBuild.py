from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

bp_charBuild = Blueprint("bp_charBuild", __name__)


@bp_charBuild.route("/charBuild/setDefaultSkill", methods=["POST"])
@player_data_decorator
def charBuild_setDefaultSkill(player_data):
    request_json = request.get_json()

    char_num_id = request_json["charInstId"]
    default_skill_index = request_json["defaultSkillIndex"]

    player_data["troop"]["chars"][str(char_num_id)]["defaultSkillIndex"] = (
        default_skill_index
    )

    response = {}
    return response


@bp_charBuild.route("/charBuild/setEquipment", methods=["POST"])
@player_data_decorator
def charBuild_setEquipment(player_data):
    request_json = request.get_json()

    char_num_id = request_json["charInstId"]
    equip_id = request_json["equipId"]

    player_data["troop"]["chars"][str(char_num_id)]["currentEquip"] = equip_id

    response = {}
    return response


@bp_charBuild.route("/charBuild/setCharVoiceLan", methods=["POST"])
@player_data_decorator
def charBuild_setCharVoiceLan(player_data):
    request_json = request.get_json()

    for char_num_id in request_json["charList"]:
        player_data["troop"]["chars"][str(char_num_id)]["voiceLan"] = request_json[
            "voiceLan"
        ]

    response = {}
    return response


@bp_charBuild.route("/charBuild/changeCharSkin", methods=["POST"])
@player_data_decorator
def charBuild_changeCharSkin(player_data):
    request_json = request.get_json()

    char_num_id = request_json["charInstId"]
    skin_id = request_json["skinId"]

    player_data["troop"]["chars"][str(char_num_id)]["skin"] = skin_id

    response = {}
    return response
