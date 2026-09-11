import requests
import json

from ..const.filepath import VERSION_JSON_CN, VERSION_WINDOWS_JSON_CN
from ..const.filepath import VERSION_JSON_EN, VERSION_WINDOWS_JSON_EN
from ..const.region import GameRegion

REQUESTS_TIMEOUT = 60


def get_version(game_region: GameRegion):
    try:
        match game_region:
            case GameRegion.GAME_REGION_CN:
                url = "https://ak-conf.hypergryph.com/config/prod/official/Android/version"
            case GameRegion.GAME_REGION_EN:
                url = "https://ark-us-static-online.yo-star.com/assetbundle/official/Android/version"

        server_version = requests.get(
            url,
            timeout=REQUESTS_TIMEOUT,
        ).json()
        if "resVersion" in server_version and "clientVersion" in server_version:
            return server_version
        return None
    except Exception:
        return None


def get_pc_version(game_region: GameRegion):
    try:
        match game_region:
            case GameRegion.GAME_REGION_CN:
                url = "https://ak-conf.hypergryph.com/config/prod/official/Windows/version"
            case GameRegion.GAME_REGION_EN:
                url = "https://ark-us-static-online.yo-star.com/assetbundle/official/Windows/version"

        server_version = requests.get(
            url,
            timeout=REQUESTS_TIMEOUT,
        ).json()
        if "resVersion" in server_version and "clientVersion" in server_version:
            return server_version
        return None
    except Exception:
        return None


def get_func_ver(game_region: GameRegion):
    try:
        match game_region:
            case GameRegion.GAME_REGION_CN:
                url = (
                    "https://ak-conf.hypergryph.com/config/prod/official/network_config"
                )
            case GameRegion.GAME_REGION_EN:
                url = "https://ak-conf.arknights.global/config/prod/official/network_config"

        server_network_config = requests.get(
            url,
            timeout=REQUESTS_TIMEOUT,
        ).json()
        if "content" in server_network_config:
            server_network_config = json.loads(server_network_config["content"])
            func_ver = "V050"
            for cur_func_ver in server_network_config["configs"]:
                func_ver = max(func_ver, cur_func_ver)
            return func_ver
        return None
    except Exception:
        return None


def main():
    # CN

    with open(VERSION_JSON_CN, encoding="utf-8") as f:
        version_json_obj = json.load(f)

    server_version = get_version(GameRegion.GAME_REGION_CN)

    if server_version is not None:
        version_json_obj["version"] = server_version

    func_ver = get_func_ver(GameRegion.GAME_REGION_CN)

    if func_ver is not None:
        version_json_obj["funcVer"] = func_ver

    with open(VERSION_JSON_CN, "w", encoding="utf-8") as f:
        json.dump(version_json_obj, f, ensure_ascii=False, indent=4)

    # ----------

    with open(VERSION_WINDOWS_JSON_CN, encoding="utf-8") as f:
        version_windows_json_obj = json.load(f)

    pc_server_version = get_pc_version(GameRegion.GAME_REGION_CN)

    if pc_server_version is not None:
        version_windows_json_obj["version"] = pc_server_version

    with open(VERSION_WINDOWS_JSON_CN, "w", encoding="utf-8") as f:
        json.dump(version_windows_json_obj, f, ensure_ascii=False, indent=4)

    # EN

    with open(VERSION_JSON_EN, encoding="utf-8") as f:
        version_json_obj = json.load(f)

    server_version = get_version(GameRegion.GAME_REGION_EN)

    if server_version is not None:
        version_json_obj["version"] = server_version

    func_ver = get_func_ver(GameRegion.GAME_REGION_EN)

    if func_ver is not None:
        version_json_obj["funcVer"] = func_ver

    with open(VERSION_JSON_EN, "w", encoding="utf-8") as f:
        json.dump(version_json_obj, f, ensure_ascii=False, indent=4)

    # ----------

    with open(VERSION_WINDOWS_JSON_EN, encoding="utf-8") as f:
        version_windows_json_obj = json.load(f)

    pc_server_version = get_pc_version(GameRegion.GAME_REGION_EN)

    if pc_server_version is not None:
        version_windows_json_obj["version"] = pc_server_version

    with open(VERSION_WINDOWS_JSON_EN, "w", encoding="utf-8") as f:
        json.dump(version_windows_json_obj, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
