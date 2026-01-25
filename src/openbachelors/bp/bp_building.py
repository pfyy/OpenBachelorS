from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

router = APIRouter()


@router.post("/building/sync")
@player_data_decorator
async def building_sync(player_data, request: Request):
    request_json = await request.json()
    response = {}
    return response


@router.post("/building/getRecentVisitors")
async def building_getRecentVisitors(request: Request):
    request_json = await request.json()
    response = {"visitors": []}
    return response


@router.post("/building/getInfoShareVisitorsNum")
async def building_getInfoShareVisitorsNum(request: Request):
    request_json = await request.json()
    response = {"num": 0}
    return response


@router.post("/building/getClueFriendList")
@player_data_decorator
async def building_getClueFriendList(player_data, request: Request):
    request_json = await request.json()
    response = {"result": []}
    return response


@router.post("/building/getClueBox")
@player_data_decorator
async def building_getClueBox(player_data, request: Request):
    request_json = await request.json()
    response = {"box": []}
    return response


@router.post("/building/getAssistReport")
@player_data_decorator
async def building_getAssistReport(player_data, request: Request):
    request_json = await request.json()
    response = {"reports": []}
    return response


@router.post("/building/changeDiySolution")
@player_data_decorator
async def building_changeDiySolution(player_data, request: Request):
    request_json = await request.json()

    room_id = request_json["roomSlotId"]
    diy_solution = request_json["solution"]

    room_type = player_data["building"]["roomSlots"][room_id]["roomId"]

    player_data["building"]["rooms"][room_type][room_id]["diySolution"] = diy_solution

    response = {}
    return response


@router.post("/building/setBuildingAssist")
@player_data_decorator
async def building_setBuildingAssist(player_data, request: Request):
    request_json = await request.json()

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


@router.post("/building/assignChar")
@player_data_decorator
async def building_assignChar(player_data, request: Request):
    request_json = await request.json()

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


@router.post("/building/getMessageBoardContent")
@player_data_decorator
async def building_getMessageBoardContent(player_data, request: Request):
    request_json = await request.json()

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


@router.post("/building/changeBGM")
@player_data_decorator
async def building_changeBGM(player_data, request: Request):
    request_json = await request.json()

    music_id = request_json["musicId"]

    player_data["building"]["music"]["selected"] = music_id

    response = {}
    return response


@router.post("/building/setPrivateDormOwner")
@player_data_decorator
async def building_setPrivateDormOwner(player_data, request: Request):
    request_json = await request.json()

    room_id = request_json["slotId"]
    char_num_id = request_json["charInsId"]

    player_data["building"]["rooms"]["PRIVATE"][room_id]["owners"] = [char_num_id]

    response = {}
    return response


@router.post("/building/saveDiyPresetSolution")
@player_data_decorator
async def building_saveDiyPresetSolution(player_data, request: Request):
    request_json = await request.json()

    solution_id = request_json["solutionId"]

    player_data["building"]["diyPresetSolutions"][str(solution_id)] = {
        "name": request_json["name"],
        "solution": request_json["solution"],
        "roomType": request_json["roomType"],
        "thumbnail": "http://127.0.0.1/thumbnail.jpg",
    }

    response = {}
    return response


@router.post("/building/getThumbnailUrl")
async def building_getThumbnailUrl(request: Request):
    request_json = await request.json()

    response = {"url": ["http://127.0.0.1/thumbnail.jpg"]}
    return response


@router.post("/building/changePresetName")
@player_data_decorator
async def building_changePresetName(player_data, request: Request):
    request_json = await request.json()

    solution_id = request_json["solutionId"]

    player_data["building"]["diyPresetSolutions"][str(solution_id)]["name"] = (
        request_json["name"]
    )

    response = {}
    return response
