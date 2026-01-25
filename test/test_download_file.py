import pytest

from openbachelors.const.filepath import ASSET_DIRPATH
from openbachelors.util.helper import download_file


@pytest.mark.asyncio
async def test_download_file():
    await download_file(
        "https://dl.google.com/tag/s/dl/chrome/install/googlechromestandaloneenterprise64.msi",
        "chrome.exe",
        ASSET_DIRPATH,
    )
