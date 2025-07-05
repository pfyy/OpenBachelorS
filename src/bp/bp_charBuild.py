from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, CHARWORD_TABLE
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator, char_id_lst, player_data_template
from ..util.helper import get_char_num_id
from ..util.battle_log_logger import log_battle_log_if_necessary

bp_charBuild = Blueprint("bp_charBuild", __name__)


@bp_charBuild.route("/charBuild/setDefaultSkill", methods=["POST"])
@player_data_decorator
def charBuild_setDefaultSkill(player_data):
    request_json = request.get_json()

    char_num_id = request_json["charInstId"]
    default_skill_index = request_json["defaultSkillIndex"]

    if (
        "currentTmpl" in player_data["troop"]["chars"][str(char_num_id)]
        and player_data["troop"]["chars"][str(char_num_id)]["currentTmpl"] is not None
    ):
        tmpl_id = player_data["troop"]["chars"][str(char_num_id)]["currentTmpl"]
        player_data["troop"]["chars"][str(char_num_id)]["tmpl"][tmpl_id][
            "defaultSkillIndex"
        ] = default_skill_index
    else:
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

    if (
        "currentTmpl" in player_data["troop"]["chars"][str(char_num_id)]
        and player_data["troop"]["chars"][str(char_num_id)]["currentTmpl"] is not None
    ):
        tmpl_id = player_data["troop"]["chars"][str(char_num_id)]["currentTmpl"]
        player_data["troop"]["chars"][str(char_num_id)]["tmpl"][tmpl_id][
            "currentEquip"
        ] = equip_id
    else:
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

    if (
        "currentTmpl" in player_data["troop"]["chars"][str(char_num_id)]
        and player_data["troop"]["chars"][str(char_num_id)]["currentTmpl"] is not None
    ):
        tmpl_id = player_data["troop"]["chars"][str(char_num_id)]["currentTmpl"]
        player_data["troop"]["chars"][str(char_num_id)]["tmpl"][tmpl_id]["skinId"] = (
            skin_id
        )
    else:
        player_data["troop"]["chars"][str(char_num_id)]["skin"] = skin_id

    response = {}
    return response


@bp_charBuild.route("/charBuild/batchSetCharVoiceLan", methods=["POST"])
@player_data_decorator
def charBuild_batchSetCharVoiceLan(player_data):
    request_json = request.get_json()
    target_voice_lan = request_json["voiceLan"]

    charword_table = const_json_loader[CHARWORD_TABLE]

    char_id_set = set(char_id_lst.copy())

    for char_id, voice_lan_obj in charword_table["voiceLangDict"]:
        if char_id not in char_id_set:
            continue

        char_num_id = get_char_num_id(char_id)

        if target_voice_lan in voice_lan_obj["dict"]:
            voice_lan = target_voice_lan
        else:
            voice_lan = player_data_template["troop"]["chars"][str(char_num_id)][
                "voiceLan"
            ]

        player_data["troop"]["chars"][str(char_num_id)]["voiceLan"] = voice_lan

    response = {}
    return response


@bp_charBuild.route("/charBuild/changeCharTemplate", methods=["POST"])
@player_data_decorator
def charBuild_changeCharTemplate(player_data):
    request_json = request.get_json()

    char_num_id = request_json["charInstId"]
    tmpl_id = request_json["templateId"]

    player_data["troop"]["chars"][str(char_num_id)]["currentTmpl"] = tmpl_id

    response = {}
    return response


@bp_charBuild.route("/charBuild/addonStage/battleStart", methods=["POST"])
@player_data_decorator
def charBuild_addonStage_battleStart(player_data):
    request_json = request.get_json()

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@bp_charBuild.route("/charBuild/addonStage/battleFinish", methods=["POST"])
@player_data_decorator
def charBuild_addonStage_battleFinish(player_data):
    request_json = request.get_json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "firstRewards": [],
    }
    return response


@bp_charBuild.route("/charBuild/changeSkinSpState", methods=["POST"])
@player_data_decorator
def charBuild_changeSkinSpState(player_data):
    request_json = request.get_json()

    skin_id = request_json["skinId"]

    player_data["skin"]["skinSp"][skin_id] = request_json["isSpecial"]

    response = {}
    return response
