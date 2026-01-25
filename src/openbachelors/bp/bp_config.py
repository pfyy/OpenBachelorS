import json
from uuid import uuid4

from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, VERSION_WINDOWS_JSON
from ..util.const_json_loader import const_json_loader
from ..util.server_url import get_server_url


router = APIRouter()


@router.get("/config/prod/official/network_config")
async def config_prod_official_network_config(request: Request):
    url = get_server_url(request)

    funcVer = const_json_loader[VERSION_JSON]["funcVer"]

    content_obj = {
        "configVer": "5",
        "funcVer": funcVer,
        "configs": {},
    }

    funcVer_num = int(funcVer[1:])

    for i in range(10):
        cur_funcVer = f"V{funcVer_num - i:03}"
        content_obj["configs"][cur_funcVer] = {
            "override": true,
            "network": {
                "gs": f"{url}",
                "as": f"{url}",
                "u8": f"{url}/u8",
                "hu": f"{url}/assetbundle/official",
                "hv": f"{url}/config/prod/official/{{0}}/version",
                "rc": f"{url}/config/prod/official/remote_config",
                "an": f"{url}/config/prod/announce_meta/{{0}}/announcement.meta.json",
                "prean": f"{url}/config/prod/announce_meta/{{0}}/preannouncement.meta.json",
                "sl": f"{url}/protocol/service",
                "of": f"{url}/index.html",
                "pkgAd": f"{url}/download",
                "pkgIOS": f"{url}/cn/app/id1454663939",
                "secure": false,
            },
        }

    content = json.dumps(content_obj)
    response = {
        "sign": "fake",
        "content": content,
    }
    return response


@router.get("/config/prod/official/remote_config")
async def config_prod_official_remote_config(request: Request):
    return {}


@router.get("/api/remote_config/1/prod/default/Android/remote_config")
async def api_remote_config_1_prod_default_Android_remote_config(request: Request):
    return {}


@router.get("/config/prod/official/Android/version")
async def config_prod_official_Android_version(request: Request):
    version = const_json_loader[VERSION_JSON]["version"].copy()
    if const_json_loader[CONFIG_JSON]["mod"]:
        src_res_version = version["resVersion"]
        if "_" in src_res_version:
            src_res_version_prefix = src_res_version.rpartition("_")[0]
        else:
            src_res_version_prefix = src_res_version.rpartition("-")[0]
        dst_res_version = f"{src_res_version_prefix}-{uuid4().hex[:6]}"
        version["resVersion"] = dst_res_version
    return version


@router.get("/config/prod/official/Windows/version")
async def config_prod_official_Windows_version(request: Request):
    version = const_json_loader[VERSION_WINDOWS_JSON]["version"].copy()
    if const_json_loader[CONFIG_JSON]["mod"]:
        src_res_version = version["resVersion"]
        if "_" in src_res_version:
            src_res_version_prefix = src_res_version.rpartition("_")[0]
        else:
            src_res_version_prefix = src_res_version.rpartition("-")[0]
        dst_res_version = f"{src_res_version_prefix}-{uuid4().hex[:6]}"
        version["resVersion"] = dst_res_version
    return version


@router.get("/config/prod/announce_meta/Android/preannouncement.meta.json")
async def config_prod_announce_meta_Android_preannouncement_meta_json(request: Request):
    url = get_server_url(request)

    response = {
        "preAnnounceId": "478",
        "actived": true,
        "preAnnounceType": 2,
        "preAnnounceUrl": f"{url}/announce/Android/preannouncement/478_1730418060.html",
    }
    return response
