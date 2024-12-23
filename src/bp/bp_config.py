import json

from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader


bp_config = Blueprint("bp_config", __name__)


@bp_config.route("/config/prod/official/network_config")
def config_prod_official_network_config():
    host = const_json_loader[CONFIG_JSON]["host"]
    port = const_json_loader[CONFIG_JSON]["port"]
    url = f"http://{host}:{port}"

    funcVer = const_json_loader[VERSION_JSON]["funcVer"]

    content_obj = {
        "configVer": "5",
        "funcVer": funcVer,
        "configs": {
            funcVer: {
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
            },
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
    return version
