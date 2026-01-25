from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, ASSIST_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.helper import (
    get_char_num_id,
    get_friend_uid_from_assist_lst_idx,
    get_assist_lst_idx_from_friend_uid,
    convert_char_obj_to_assist_char_obj,
    get_friend_uid_from_assist_lst_idx_ext,
    get_assist_lst_idx_from_friend_uid_ext,
)
from ..util.assist_ext import profession_lst, profession_assist_lst_dict

router = APIRouter()


@router.post("/businessCard/getOtherPlayerNameCard")
@player_data_decorator
async def businessCard_getOtherPlayerNameCard(player_data, request: Request):
    request_json = await request.json()

    friend_uid = request_json["uid"]

    if const_json_loader[CONFIG_JSON]["assist_ext"]:
        profession_idx, assist_lst_idx = get_assist_lst_idx_from_friend_uid_ext(
            friend_uid
        )
        profession = profession_lst[profession_idx]
        assist_lst = profession_assist_lst_dict[profession].copy()
    else:
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
                "skin": {"selected": "nc_rhodes_default", "state": {}, "tmpl": {}},
                "misc": {"showDetail": true, "showBirthday": false},
            },
        }
    }
    return response


@router.post("/businessCard/editNameCard")
@player_data_decorator
async def businessCard_editNameCard(player_data, request: Request):
    request_json = await request.json()

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
