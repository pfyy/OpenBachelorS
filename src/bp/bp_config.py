import json
from uuid import uuid4

from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.server_url import get_server_url


bp_config = Blueprint("bp_config", __name__)


@bp_config.route("/config/prod/official/network_config")
def config_prod_official_network_config():
    url = get_server_url()

    funcVer = const_json_loader[VERSION_JSON]["funcVer"]

    content_obj = {
        "configVer": "5",
        "funcVer": funcVer,
        "configs": {},
    }

    funcVer_num = int(funcVer[1:])

    for i in range(10):
        cur_funcVer = f"V{funcVer_num-i:03}"
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


@bp_config.route("/config/prod/official/remote_config")
def config_prod_official_remote_config():
    return {}


@bp_config.route("/config/prod/official/Android/version")
def config_prod_official_Android_version():
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


@bp_config.route("/config/prod/announce_meta/Android/preannouncement.meta.json")
def config_prod_announce_meta_Android_preannouncement_meta_json():
    url = get_server_url()

    response = {
        "preAnnounceId": "478",
        "actived": true,
        "preAnnounceType": 2,
        "preAnnounceUrl": f"{url}/announce/Android/preannouncement/478_1730418060.html",
    }
    return response
