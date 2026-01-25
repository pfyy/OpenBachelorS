import os
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys
import asyncio
import logging


from ..app import app
from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, ASSET_DIRPATH
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
    res_version, asset_filename = worker_param

    logger.info(f"downloading {asset_filename}")

    try:
        ret_val = await download_asset(res_version, asset_filename, "Android")
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
    return asset_download_worker_loop.run_until_complete(
        async_asset_download_worker_func(worker_param)
    )


def main():
    res_version = const_json_loader[VERSION_JSON]["version"]["resVersion"]

    download_all = False
    if "--download_all" in sys.argv:
        download_all = True

    asyncio.run(download_asset(res_version, HOT_UPDATE_LIST_JSON, "Android"))
    with open(
        os.path.join(ASSET_DIRPATH, res_version, HOT_UPDATE_LIST_JSON),
        encoding="utf-8",
    ) as f:
        hot_update_list = json.load(f)

    asset_filename_lst = []

    for ab_obj in hot_update_list["abInfos"]:
        ab_filename = get_asset_filename(ab_obj["name"])

        if not download_all:
            pid = ab_obj.get("pid")
            if (
                pid
                and pid != "lpack_lcom"
                and not pid.startswith("lpack_init")
                and pid != "lpack_char"
                and pid != "lpack_furn"
            ):
                continue

        asset_filename_lst.append(ab_filename)

    for pack_obj in hot_update_list["packInfos"]:
        pack_filename = get_asset_filename(pack_obj["name"])

        asset_filename_lst.append(pack_filename)

    future_lst = []
    ret_val_lst = []

    try:
        with ProcessPoolExecutor(
            NUM_ASSET_DOWNLOAD_WORKER,
            initializer=init_asset_download_worker,
        ) as pool:
            for asset_filename in asset_filename_lst:
                future_lst.append(
                    pool.submit(
                        asset_download_worker_func, (res_version, asset_filename)
                    )
                )

                for future in as_completed(future_lst):
                    ret_val_lst.append(future.result())
    except KeyboardInterrupt:
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
