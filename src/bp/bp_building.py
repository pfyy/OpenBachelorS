from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

bp_building = Blueprint("bp_building", __name__)


@bp_building.route("/building/sync", methods=["POST"])
@player_data_decorator
def building_sync(player_data):
    request_json = request.get_json()
    response = {}
    return response


@bp_building.route("/building/getRecentVisitors", methods=["POST"])
def building_getRecentVisitors():
    request_json = request.get_json()
    response = {"visitors": []}
    return response


@bp_building.route("/building/getInfoShareVisitorsNum", methods=["POST"])
def building_getInfoShareVisitorsNum():
    request_json = request.get_json()
    response = {"num": 0}
    return response


@bp_building.route("/building/getClueFriendList", methods=["POST"])
@player_data_decorator
def building_getClueFriendList(player_data):
    request_json = request.get_json()
    response = {"result": []}
    return response


@bp_building.route("/building/getClueBox", methods=["POST"])
@player_data_decorator
def building_getClueBox(player_data):
    request_json = request.get_json()
    response = {"box": []}
    return response


@bp_building.route("/building/getAssistReport", methods=["POST"])
@player_data_decorator
def building_getAssistReport(player_data):
    request_json = request.get_json()
    response = {"reports": []}
    return response


@bp_building.route("/building/changeDiySolution", methods=["POST"])
@player_data_decorator
def building_changeDiySolution(player_data):
    request_json = request.get_json()

    room_id = request_json["roomSlotId"]
    diy_solution = request_json["solution"]

    room_type = player_data["building"]["roomSlots"][room_id]["roomId"]

    player_data["building"]["rooms"][room_type][room_id]["diySolution"] = diy_solution

    response = {}
    return response


@bp_building.route("/building/setBuildingAssist", methods=["POST"])
@player_data_decorator
def building_setBuildingAssist(player_data):
    request_json = request.get_json()

    char_num_id = request_json["charInstId"]
    assist_idx = request_json["type"]

    assist_lst = player_data["building"]["assist"].copy()
    if char_num_id != -1:
        for i in range(len(assist_lst)):
            if assist_lst[i] == char_num_id:
                assist_lst[i] = -1
    assist_lst[assist_idx] = char_num_id
    player_data["building"]["assist"] = assist_lst

    response = {}
    return response


@bp_building.route("/building/assignChar", methods=["POST"])
@player_data_decorator
def building_assignChar(player_data):
    request_json = request.get_json()

    room_id = request_json["roomSlotId"]
    char_num_id_lst = request_json["charInstIdList"]

    old_char_num_id_lst = player_data["building"]["roomSlots"][room_id][
        "charInstIds"
    ].copy()

    for char_num_id in old_char_num_id_lst:
        if char_num_id == -1:
            continue
        player_data["building"]["chars"][str(char_num_id)]["roomSlotId"] = ""
        player_data["building"]["chars"][str(char_num_id)]["index"] = -1

    for char_idx, char_num_id in enumerate(char_num_id_lst):
        if char_num_id == -1:
            continue
        src_room_id = player_data["building"]["chars"][str(char_num_id)]["roomSlotId"]
        if src_room_id:
            src_char_idx = player_data["building"]["chars"][str(char_num_id)]["index"]

            src_char_num_id_lst = player_data["building"]["roomSlots"][src_room_id][
                "charInstIds"
            ].copy()
            src_char_num_id_lst[src_char_idx] = -1
            player_data["building"]["roomSlots"][src_room_id]["charInstIds"] = (
                src_char_num_id_lst
            )
        player_data["building"]["chars"][str(char_num_id)]["roomSlotId"] = room_id
        player_data["building"]["chars"][str(char_num_id)]["index"] = char_idx

    player_data["building"]["roomSlots"][room_id]["charInstIds"] = char_num_id_lst

    response = {}
    return response


@bp_building.route("/building/getMessageBoardContent", methods=["POST"])
@player_data_decorator
def building_getMessageBoardContent(player_data):
    request_json = request.get_json()

    response = {
        "thisWeekVisitors": [],
        "lastWeekVisitors": [],
        "todayVisit": 0,
        "weeklyVisit": 0,
        "lastWeekVisit": 0,
        "lastWeekSpReward": 0,
        "lastShowTs": 1700000000,
    }
    return response


@bp_building.route("/building/changeBGM", methods=["POST"])
@player_data_decorator
def building_changeBGM(player_data):
    request_json = request.get_json()

    music_id = request_json["musicId"]

    player_data["building"]["music"]["selected"] = music_id

    response = {}
    return response


@bp_building.route("/building/setPrivateDormOwner", methods=["POST"])
@player_data_decorator
def building_setPrivateDormOwner(player_data):
    request_json = request.get_json()

    room_id = request_json["slotId"]
    char_num_id = request_json["charInsId"]

    player_data["building"]["rooms"]["PRIVATE"][room_id]["owners"] = [char_num_id]

    response = {}
    return response


@bp_building.route("/building/saveDiyPresetSolution", methods=["POST"])
@player_data_decorator
def building_saveDiyPresetSolution(player_data):
    request_json = request.get_json()

    solution_id = request_json["solutionId"]

    player_data["building"]["diyPresetSolutions"][str(solution_id)] = {
        "name": request_json["name"],
        "solution": request_json["solution"],
        "roomType": request_json["roomType"],
        "thumbnail": "http://127.0.0.1/thumbnail.jpg",
    }

    response = {}
    return response


@bp_building.route("/building/getThumbnailUrl", methods=["POST"])
def building_getThumbnailUrl():
    request_json = request.get_json()

    response = {"url": ["http://127.0.0.1/thumbnail.jpg"]}
    return response


@bp_building.route("/building/changePresetName", methods=["POST"])
@player_data_decorator
def building_changePresetName(player_data):
    request_json = request.get_json()

    solution_id = request_json["solutionId"]

    player_data["building"]["diyPresetSolutions"][str(solution_id)]["name"] = (
        request_json["name"]
    )

    response = {}
    return response
