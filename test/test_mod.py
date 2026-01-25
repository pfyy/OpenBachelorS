import os
import json

import requests

from openbachelors.const.filepath import TMP_DIRPATH
from openbachelors.util.mod_loader import mod_loader


def test_mod_loader():
    src_hot_update_list = requests.get(
        "https://ak.hycdn.cn/assetbundle/official/Android/assets/24-12-28-16-17-06-54bd34/hot_update_list.json"
    ).json()
    mod_loader.build_hot_update_list(src_hot_update_list)
    assert mod_loader.hot_update_list is not None
    os.makedirs(TMP_DIRPATH, exist_ok=True)
    with open(
        os.path.join(TMP_DIRPATH, "hot_update_list.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(mod_loader.hot_update_list.copy(), f, ensure_ascii=False, indent=4)
