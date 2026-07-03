import os
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys
import asyncio
import logging
from tkinter.filedialog import askopenfilename
from pathlib import Path
import zipfile

from ..app import app
from ..const.json_const import true, false, null
from ..const.filepath import (
    CONFIG_JSON,
    VERSION_JSON,
    ASSET_DIRPATH,
    VERSION_WINDOWS_JSON,
)
from ..util.const_json_loader import const_json_loader
from ..bp.bp_assetbundle import (
    download_asset,
    HOT_UPDATE_LIST_JSON,
    DownloadAssetResult,
)
from ..util.helper import get_asset_filename

logger = logging.getLogger(__name__)

NUM_ASSET_DOWNLOAD_WORKER = 8


async def async_asset_download_worker_func(worker_param):
    res_version, asset_filename, platform_name = worker_param

    logger.info(f"downloading {asset_filename}")

    try:
        ret_val = await download_asset(res_version, asset_filename, platform_name)
    except Exception as e:
        logger.error(f"exception during download of {asset_filename}: {e}")
        return asset_filename

    if isinstance(ret_val, DownloadAssetResult.HttpStatusCode):
        logger.error(f"failed to download {asset_filename}")
        return asset_filename

    logger.info(f"downloaded {asset_filename}")

    return None


asset_download_worker_loop = None


def init_asset_download_worker():
    global asset_download_worker_loop

    asset_download_worker_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(asset_download_worker_loop)


def asset_download_worker_func(worker_param):
    try:
        return asset_download_worker_loop.run_until_complete(
            async_asset_download_worker_func(worker_param)
        )
    except KeyboardInterrupt:
        logger.warning("child proc keyboard interrupt")
        os._exit(1)


def get_asset_filename_lst_full(hot_update_list):
    asset_filename_lst = []

    for ab_obj in hot_update_list["abInfos"]:
        ab_filename = get_asset_filename(ab_obj["name"])

        asset_filename_lst.append(ab_filename)

    for pack_obj in hot_update_list["packInfos"]:
        pack_filename = get_asset_filename(pack_obj["name"])

        asset_filename_lst.append(pack_filename)

    return asset_filename_lst


def get_ab_dict(hot_update_list):
    ab_dict = {}

    for ab_obj in hot_update_list["abInfos"]:
        ab_name = ab_obj["name"]
        ab_hash = ab_obj["hash"]
        ab_md5 = ab_obj["md5"]

        ab_dict[ab_name] = ab_hash, ab_md5

    return ab_dict


def get_pack_ab_dict(hot_update_list):
    pack_ab_dict = {}
    ab_pack_dict = {}
    for ab_obj in hot_update_list["abInfos"]:
        ab_name = ab_obj["name"]
        pack_id = ab_obj.get("pid")

        if not pack_id:
            continue

        if pack_id not in pack_ab_dict:
            pack_ab_dict[pack_id] = set()

        pack_ab_dict[pack_id].add(ab_name)
        ab_pack_dict[ab_name] = pack_id

    return pack_ab_dict, ab_pack_dict


def get_asset_filename_lst_exclude_local(local_hot_update_list, hot_update_list):
    asset_filename_lst = []

    local_ab_dict = get_ab_dict(local_hot_update_list)
    ab_dict = get_ab_dict(hot_update_list)

    download_ab_name_lst = []

    for ab_name, (ab_hash, ab_md5) in ab_dict.items():
        local_ab_hash, local_ab_md5 = local_ab_dict.get(ab_name, (None, None))
        if not (local_ab_hash == ab_hash or local_ab_md5 == ab_md5):
            download_ab_name_lst.append(ab_name)

    pack_ab_dict, ab_pack_dict = get_pack_ab_dict(hot_update_list)

    used_pack_dict = {}

    for ab_name in download_ab_name_lst:
        pack_id = ab_pack_dict.get(ab_name)

        if not pack_id:
            continue

        if pack_id not in used_pack_dict:
            used_pack_dict[pack_id] = set()
        used_pack_dict[pack_id].add(ab_name)

    download_pack_id_set = set()

    for pack_id in used_pack_dict:
        if len(used_pack_dict[pack_id]) == len(pack_ab_dict[pack_id]):
            download_pack_id_set.add(pack_id)

    for ab_name in download_ab_name_lst:
        pack_id = ab_pack_dict.get(ab_name)
        if pack_id and pack_id in download_pack_id_set:
            continue

        ab_filename = get_asset_filename(ab_name)

        asset_filename_lst.append(ab_filename)

    for pack_id in download_pack_id_set:
        pack_filename = get_asset_filename(pack_id)

        asset_filename_lst.append(pack_filename)

    return asset_filename_lst


def main():
    platform_name = "Android"
    res_version = const_json_loader[VERSION_JSON]["version"]["resVersion"]

    if "--windows" in sys.argv:
        platform_name = "Windows"
        res_version = const_json_loader[VERSION_WINDOWS_JSON]["version"]["resVersion"]

    download_all = False
    if "--download_all" in sys.argv:
        download_all = True

    if not download_all:
        match platform_name:
            case "Android":
                apk_filepath = askopenfilename(
                    filetypes=[("APK", ".apk")],
                )

                with zipfile.ZipFile(apk_filepath) as f:
                    local_hot_update_list = json.loads(
                        f.read("assets/AB/Android/hot_update_list.json")
                    )
            case "Windows":
                exe_filepath = askopenfilename(
                    filetypes=[("Arknights", "Arknights.exe")],
                )

                local_hot_update_list = json.loads(
                    (
                        Path(exe_filepath).parent
                        / "Arknights_Data"
                        / "StreamingAssets"
                        / "AB"
                        / "Windows"
                        / "hot_update_list.json"
                    ).read_text(encoding="utf-8")
                )

    asyncio.run(download_asset(res_version, HOT_UPDATE_LIST_JSON, platform_name))
    with open(
        os.path.join(ASSET_DIRPATH, res_version, HOT_UPDATE_LIST_JSON),
        encoding="utf-8",
    ) as f:
        hot_update_list = json.load(f)

    if download_all:
        asset_filename_lst = get_asset_filename_lst_full(hot_update_list)
    else:
        asset_filename_lst = get_asset_filename_lst_exclude_local(
            local_hot_update_list, hot_update_list
        )

    logger.info(f"# file to download: {len(asset_filename_lst)}")

    future_lst = []
    ret_val_lst = []

    try:
        pool = ProcessPoolExecutor(
            NUM_ASSET_DOWNLOAD_WORKER,
            initializer=init_asset_download_worker,
        )
        for asset_filename in asset_filename_lst:
            future_lst.append(
                pool.submit(
                    asset_download_worker_func,
                    (res_version, asset_filename, platform_name),
                )
            )

        for future in as_completed(future_lst):
            ret_val_lst.append(future.result())

        pool.shutdown()
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        logger.warning("keyboard interrupt")
        sys.exit(1)

    logger.info("--- summary ---")

    err_flag = False

    for ret_val in ret_val_lst:
        if ret_val is None:
            continue

        err_flag = True

        logger.error(f"failed to download {ret_val}")

    if not err_flag:
        logger.info("success")


if __name__ == "__main__":
    main()
