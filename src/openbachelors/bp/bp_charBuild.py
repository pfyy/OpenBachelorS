from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, CHARWORD_TABLE
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator, char_id_lst, player_data_template
from ..util.helper import get_char_num_id
from ..util.battle_log_logger import log_battle_log_if_necessary

router = APIRouter()


@router.post("/charBuild/setDefaultSkill")
@player_data_decorator
async def charBuild_setDefaultSkill(player_data, request: Request):
    request_json = await request.json()

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


@router.post("/charBuild/setEquipment")
@player_data_decorator
async def charBuild_setEquipment(player_data, request: Request):
    request_json = await request.json()

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


@router.post("/charBuild/setCharVoiceLan")
@player_data_decorator
async def charBuild_setCharVoiceLan(player_data, request: Request):
    request_json = await request.json()

    for char_num_id in request_json["charList"]:
        player_data["troop"]["chars"][str(char_num_id)]["voiceLan"] = request_json[
            "voiceLan"
        ]

    response = {}
    return response


@router.post("/charBuild/changeCharSkin")
@player_data_decorator
async def charBuild_changeCharSkin(player_data, request: Request):
    request_json = await request.json()

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


@router.post("/charBuild/batchSetCharVoiceLan")
@player_data_decorator
async def charBuild_batchSetCharVoiceLan(player_data, request: Request):
    request_json = await request.json()
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


@router.post("/charBuild/changeCharTemplate")
@player_data_decorator
async def charBuild_changeCharTemplate(player_data, request: Request):
    request_json = await request.json()

    char_num_id = request_json["charInstId"]
    tmpl_id = request_json["templateId"]

    player_data["troop"]["chars"][str(char_num_id)]["currentTmpl"] = tmpl_id

    response = {}
    return response


@router.post("/charBuild/addonStage/battleStart")
@player_data_decorator
async def charBuild_addonStage_battleStart(player_data, request: Request):
    request_json = await request.json()

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/charBuild/addonStage/battleFinish")
@player_data_decorator
async def charBuild_addonStage_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "firstRewards": [],
    }
    return response


@router.post("/charBuild/changeSkinSpState")
@player_data_decorator
async def charBuild_changeSkinSpState(player_data, request: Request):
    request_json = await request.json()

    skin_id = request_json["skinId"]

    player_data["skin"]["skinSp"][skin_id] = request_json["isSpecial"]

    response = {}
    return response
