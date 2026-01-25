import requests
import json

from ..const.filepath import VERSION_JSON, VERSION_WINDOWS_JSON

REQUESTS_TIMEOUT = 60


def get_version():
    try:
        server_version = requests.get(
            "https://ak-conf.hypergryph.com/config/prod/official/Android/version",
            timeout=REQUESTS_TIMEOUT,
        ).json()
        if "resVersion" in server_version and "clientVersion" in server_version:
            return server_version
        return None
    except Exception:
        return None


def get_pc_version():
    try:
        server_version = requests.get(
            "https://ak-conf.hypergryph.com/config/prod/official/Windows/version",
            timeout=REQUESTS_TIMEOUT,
        ).json()
        if "resVersion" in server_version and "clientVersion" in server_version:
            return server_version
        return None
    except Exception:
        return None


def get_func_ver():
    try:
        server_network_config = requests.get(
            "https://ak-conf.hypergryph.com/config/prod/official/network_config",
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
    with open(VERSION_JSON, encoding="utf-8") as f:
        version_json_obj = json.load(f)

    server_version = get_version()

    if server_version is not None:
        version_json_obj["version"] = server_version

    func_ver = get_func_ver()

    if func_ver is not None:
        version_json_obj["funcVer"] = func_ver

    with open(VERSION_JSON, "w", encoding="utf-8") as f:
        json.dump(version_json_obj, f, ensure_ascii=False, indent=4)

    # ----------

    with open(VERSION_WINDOWS_JSON, encoding="utf-8") as f:
        version_windows_json_obj = json.load(f)

    pc_server_version = get_pc_version()

    if pc_server_version is not None:
        version_windows_json_obj["version"] = pc_server_version

    with open(VERSION_WINDOWS_JSON, "w", encoding="utf-8") as f:
        json.dump(version_windows_json_obj, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
