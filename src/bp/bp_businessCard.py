from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, ASSIST_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.helper import (
    get_char_num_id,
    get_friend_uid_from_assist_lst_idx,
    get_assist_lst_idx_from_friend_uid,
    convert_char_obj_to_assist_char_obj,
)

bp_businessCard = Blueprint("bp_businessCard", __name__)


@bp_businessCard.route("/businessCard/getOtherPlayerNameCard", methods=["POST"])
@player_data_decorator
def businessCard_getOtherPlayerNameCard(player_data):
    request_json = request.get_json()

    friend_uid = request_json["uid"]

    assist_lst_idx = get_assist_lst_idx_from_friend_uid(friend_uid)
    assist_lst = const_json_loader[ASSIST_JSON]["assist_lst"].copy()
    assist_char_id = assist_lst[assist_lst_idx]
    assist_char_num_id = get_char_num_id(assist_char_id)

    assist_char_obj = player_data["troop"]["chars"][str(assist_char_num_id)].copy()
    convert_char_obj_to_assist_char_obj(assist_char_obj)

    response = {
        "nameCard": {
            "nickName": "Undergraduate",
            "nickNumber": "1234",
            "uid": friend_uid,
            "registerTs": 1700000000,
            "mainStageProgress": null,
            "charCnt": 0,
            "skinCnt": 0,
            "secretary": "char_002_amiya",
            "secretarySkinId": "char_002_amiya#1",
            "resume": "",
            "teamV2": {},
            "level": 120,
            "avatarId": "0",
            "avatar": {"type": "ICON", "id": "avatar_def_01"},
            "assistCharList": [assist_char_obj, null, null],
            "medalBoard": {"type": "EMPTY", "custom": null, "template": null},
            "nameCardStyle": {
                "componentOrder": ["module_sign", "module_assist", "module_medal"],
                "skin": {"selected": "nc_rhodes_default", "state": {}},
                "misc": {"showDetail": true, "showBirthday": false},
            },
        }
    }
    return response


@bp_businessCard.route("/businessCard/editNameCard", methods=["POST"])
@player_data_decorator
def businessCard_editNameCard(player_data):
    request_json = request.get_json()

    request_content = request_json["content"]

    skin_id = request_content["skinId"]
    component_order = request_content["component"]
    misc = request_content["misc"]

    if skin_id is not None:
        player_data["nameCardStyle"]["skin"]["selected"] = skin_id
        # magic number
        if request_json["flag"] & 8:
            player_data["nameCardStyle"]["skin"]["tmpl"][skin_id] = request_content[
                "skinTmpl"
            ]

    if component_order is not None:
        player_data["nameCardStyle"]["componentOrder"] = component_order

    if misc is not None:
        player_data["nameCardStyle"]["misc"]["showDetail"] = bool(misc["showDetail"])
        player_data["nameCardStyle"]["misc"]["showBirthday"] = bool(
            misc["showBirthday"]
        )

    response = {}
    return response
