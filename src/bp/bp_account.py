import os
import json

from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, TMP_DIRPATH
from ..util.const_json_loader import const_json_loader
from ..util.player_data import PlayerData, player_data_decorator
from ..util.mail_helper import get_player_mailbox
from ..util.faketime import faketime

bp_account = Blueprint("bp_account", __name__)


@bp_account.route("/account/login", methods=["POST"])
def account_login():
    request_json = request.get_json()
    token = request_json["token"]

    response = {
        "result": 0,
        "uid": "123456789",
        "secret": token,
        "serviceLicenseVersion": 0,
        "majorVersion": "354",
    }

    return response


@bp_account.route("/account/syncData", methods=["POST"])
def account_syncData():
    player_data = PlayerData()

    t = int(faketime())
    player_data["status"]["lastRefreshTs"] = t

    battle_replay_lst = player_data.battle_replay_manager.get_battle_replay_lst()
    for stage_id in battle_replay_lst:
        player_data["dungeon"]["stages"][stage_id]["hasBattleReplay"] = 1

    mail_json_obj, pending_mail_set = get_player_mailbox(player_data)
    player_data["pushFlags"]["hasGifts"] = int(bool(pending_mail_set))

    delta_response = player_data.build_delta_response()
    player_data.save()

    player_data_json_obj = player_data.copy()

    if const_json_loader[CONFIG_JSON]["debug"]:
        os.makedirs(TMP_DIRPATH, exist_ok=True)
        with open(
            os.path.join(TMP_DIRPATH, "player_data.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(player_data_json_obj, f, ensure_ascii=False, indent=4)

    response = {
        "result": 0,
        "ts": t,
        "user": player_data_json_obj,
        "playerDataDelta": {"modified": {}, "deleted": {}},
    }
    return response


@bp_account.route("/account/syncStatus", methods=["POST"])
@player_data_decorator
def account_syncStatus(player_data):
    request_json = request.get_json()
    response = {"result": {}}
    return response


@bp_account.route("/account/syncPushMessage", methods=["POST"])
@player_data_decorator
def account_syncPushMessage(player_data):
    request_json = request.get_json()
    response = {}
    return response
