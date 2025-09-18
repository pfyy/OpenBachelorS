import os
import json
from typing import Any
from dataclasses import dataclass
import asyncio

from fastapi import APIRouter
from fastapi import Request, Response
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
import aiofiles

from ..const.json_const import true, false, null
from ..const.filepath import (
    CONFIG_JSON,
    VERSION_JSON,
    ASSET_DIRPATH,
    MOD_DIRPATH,
    TMP_DIRPATH,
)
from ..util.const_json_loader import const_json_loader
from ..util.mod_loader import mod_loader
from ..util.helper import (
    is_valid_res_version,
    is_valid_asset_filename,
    download_file,
    try_get_filelock,
    release_filelock,
    get_httpx_client,
)
from ..util.log_helper import IS_DEBUG

router = APIRouter()


HOT_UPDATE_LIST_JSON = "hot_update_list.json"
ORIG_ASSET_URL_PREFIX = "https://ak.hycdn.cn/assetbundle/official/Android/assets"


class DownloadAssetResult:
    @dataclass
    class Response:
        response: Any

    @dataclass
    class HttpStatusCode:
        status_code: int

    @dataclass
    class SendFile:
        file_path: str

    @dataclass
    class Redirect:
        url: str


DownloadAssetResultType = (
    DownloadAssetResult.Response
    | DownloadAssetResult.HttpStatusCode
    | DownloadAssetResult.SendFile
    | DownloadAssetResult.Redirect
)


async def try_mod_result(res_version, asset_filename, src_res_version):
    if mod_loader.hot_update_list is None:
        await download_asset(src_res_version, HOT_UPDATE_LIST_JSON)
        async with aiofiles.open(
            os.path.join(ASSET_DIRPATH, src_res_version, HOT_UPDATE_LIST_JSON),
            encoding="utf-8",
        ) as f:
            src_hot_update_list = json.loads(await f.read())
        mod_loader.build_hot_update_list(src_hot_update_list)
    if asset_filename == HOT_UPDATE_LIST_JSON:
        hot_update_list = mod_loader.hot_update_list.copy()
        hot_update_list["versionId"] = res_version
        if IS_DEBUG:
            os.makedirs(TMP_DIRPATH, exist_ok=True)
            async with aiofiles.open(
                os.path.join(TMP_DIRPATH, HOT_UPDATE_LIST_JSON),
                "w",
                encoding="utf-8",
            ) as f:
                await f.write(json.dumps(hot_update_list, ensure_ascii=False, indent=4))
        return DownloadAssetResult.Response(response=hot_update_list)

    mod_filename = mod_loader.get_mod_filename_by_asset_filename(asset_filename)
    if mod_filename is not None:
        mod_filepath = os.path.join(MOD_DIRPATH, mod_filename)
        mod_abs_filepath = os.path.abspath(mod_filepath)
        return DownloadAssetResult.SendFile(file_path=mod_abs_filepath)

    return None


async def download_asset(res_version, asset_filename):
    if not is_valid_res_version(res_version) or not is_valid_asset_filename(
        asset_filename
    ):
        return DownloadAssetResult.HttpStatusCode(status_code=400)

    src_res_version = const_json_loader[VERSION_JSON]["version"]["resVersion"]
    if const_json_loader[CONFIG_JSON]["mod"] and res_version != src_res_version:
        mod_result = try_mod_result(res_version, asset_filename, src_res_version)

        if mod_result is not None:
            return mod_result

        # not found in mod, fall back to src res version
        res_version = src_res_version

    asset_dirpath = os.path.join(ASSET_DIRPATH, res_version)
    asset_filepath = os.path.join(asset_dirpath, asset_filename)
    asset_abs_filepath = os.path.abspath(asset_filepath)

    url = f"{ORIG_ASSET_URL_PREFIX}/{res_version}/{asset_filename}"

    while not try_get_filelock(url):
        await asyncio.sleep(10)

    try:
        if not os.path.isfile(asset_filepath):
            if (
                const_json_loader[CONFIG_JSON]["redirect_asset"]
                and asset_filename != HOT_UPDATE_LIST_JSON
            ):
                return DownloadAssetResult.Redirect(url=url)

            client = get_httpx_client()
            req = await client.head(url)

            if req.status_code != 200:
                return DownloadAssetResult.HttpStatusCode(status_code=404)

            await download_file(url, asset_filename, asset_dirpath)

        return DownloadAssetResult.SendFile(file_path=asset_abs_filepath)
    finally:
        release_filelock(url)


@router.get("/assetbundle/official/Android/assets/{res_version}/{asset_filename}")
async def assetbundle_official_Android_assets(
    res_version: str, asset_filename: str, request: Request
):
    result = await download_asset(res_version, asset_filename)

    match result:
        case DownloadAssetResult.Response(response=response):
            return response
        case DownloadAssetResult.HttpStatusCode(status_code=status_code):
            return Response(status_code=status_code)
        case DownloadAssetResult.SendFile(file_path=file_path):
            return FileResponse(file_path)
        case DownloadAssetResult.Redirect(url=url):
            return RedirectResponse(url)
        case _:
            raise AssertionError(result)
