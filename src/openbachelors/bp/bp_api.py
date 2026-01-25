from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.server_url import get_server_url


router = APIRouter()


@router.get("/api/game/get_latest_game_info")
async def api_game_get_latest_game_info(request: Request):
    client_version = const_json_loader[VERSION_JSON]["version"]["clientVersion"]

    response = {
        "version": request.query_params.get("version", ""),
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


@router.get("/api/remote_config/101/prod/default/Android/ak_sdk_config")
async def api_remote_config_101_prod_default_android_ak_sdk_config(request: Request):
    response = {}
    return response


@router.get("/api/game/get_latest")
async def api_game_get_latest(request: Request):
    response = {
        "action": 0,
        "version": "69.0.0",
        "request_version": "69.0.0",
        "pkg": {
            "packs": [],
            "total_size": "0",
            "file_path": "https://ak.hycdn.cn/GzD1CpaWgmSq1wew/69.0/update/1/1/Windows/69.0.0_OCI5nGSI9gIFzxQn/files",
            "url": "",
            "md5": "",
            "package_size": "0",
            "file_id": "0",
            "sub_channel": "1",
            "game_files_md5": "109903ea32fc4d71b6b9541bc0b5f9f0",
        },
        "patch": null,
        "state": 0,
        "launcher_action": 0,
    }
    return response


@router.get("/api/remote_config/1/prod/default/Windows/network_config")
async def api_remote_config_1_prod_default_Windows_network_config(request: Request):
    url = get_server_url(request)

    response = {
        "an": f"{url}/config/prod/announce_meta/{{0}}/announcement.meta.json",
        "as": f"{url}",
        "gs": f"{url}",
        "hu": f"{url}/assetbundle/official",
        "hv": f"{url}/config/prod/official/{{0}}/version",
        "of": f"{url}/index.html",
        "sl": f"{url}/protocol/service",
        "u8": f"{url}/u8",
        "pkgAd": f"{url}/download",
        "prean": f"{url}",
        "devsdk": false,
        "pkgIOS": "https://apps.apple.com/cn/app/id1454663939",
        "configVer": 5,
    }
    return response


@router.get("/api/remote_config/1/prod/default/Windows/remote_config")
async def api_remote_config_1_prod_default_Windows_remote_config(request: Request):
    response = {}
    return response


@router.get("/api/gate/meta/Windows")
async def api_gate_meta_Windows(request: Request):
    response = {
        "preAnnounceId": "528",
        "actived": true,
        "preAnnounceType": 2,
    }
    return response
