import os
import json

from fastapi import APIRouter
from fastapi import Request
from fastapi import Response
import aiofiles
import orjson

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, TMP_DIRPATH
from ..util.const_json_loader import const_json_loader
from ..util.player_data import PlayerData, player_data_decorator
from ..util.mail_helper import get_player_mailbox
from ..util.faketime import faketime
from ..util.log_helper import IS_DEBUG

router = APIRouter()


@router.post("/account/login")
async def account_login(request: Request):
    request_json = await request.json()
    token = request_json["token"]

    response = {
        "result": 0,
        "uid": "123456789",
        "secret": token,
        "serviceLicenseVersion": 0,
        "majorVersion": "354",
    }

    return response


@router.post("/account/syncData")
async def account_syncData(request: Request):
    player_data = await PlayerData.create(request=request)

    t = int(faketime())
    player_data["status"]["lastRefreshTs"] = t

    battle_replay_lst = await player_data.battle_replay_manager.get_battle_replay_lst()
    for stage_id in battle_replay_lst:
        player_data["dungeon"]["stages"][stage_id]["hasBattleReplay"] = 1

    mail_json_obj, pending_mail_set = get_player_mailbox(player_data)
    player_data["pushFlags"]["hasGifts"] = int(bool(pending_mail_set))

    delta_response = player_data.build_delta_response()
    await player_data.save()

    player_data_json_obj = player_data.copy()

    if IS_DEBUG:
        os.makedirs(TMP_DIRPATH, exist_ok=True)
        async with aiofiles.open(
            os.path.join(TMP_DIRPATH, "player_data.json"), "w", encoding="utf-8"
        ) as f:
            await f.write(
                json.dumps(player_data_json_obj, ensure_ascii=False, indent=4)
            )

    response = {
        "result": 0,
        "ts": t,
        "user": player_data_json_obj,
        "playerDataDelta": {"modified": {}, "deleted": {}},
    }
    return Response(content=orjson.dumps(response), media_type="application/json")


@router.post("/account/syncStatus")
@player_data_decorator
async def account_syncStatus(player_data, request: Request):
    request_json = await request.json()
    response = {"result": {}}
    return response


@router.post("/account/syncPushMessage")
@player_data_decorator
async def account_syncPushMessage(player_data, request: Request):
    request_json = await request.json()
    response = {}
    return response
