from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

bp_api = Blueprint("bp_api", __name__)


@bp_api.route("/api/game/get_latest_game_info")
def api_game_get_latest_game_info():
    client_version = const_json_loader[VERSION_JSON]["version"]["clientVersion"]

    response = {
        "version": request.args.get("version", ""),
        "action": 0,
        "update_type": 0,
        "update_info": {
            "package": null,
            "patch": null,
            "custom_info": "",
            "source_package": null,
        },
        "client_version": client_version,
    }
    return response


@bp_api.route("/api/remote_config/101/prod/default/Android/ak_sdk_config")
def api_remote_config_101_prod_default_android_ak_sdk_config():
    response = {}
    return response
