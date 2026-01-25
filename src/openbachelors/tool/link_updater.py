import requests
import json

from ..const.filepath import (
    GAME_LINK_FILEPATH,
    MUMU_LINK_FILEPATH,
    PC_GAME_LINK_FILEPATH,
)

REQUESTS_TIMEOUT = 60


def get_game_link():
    try:
        req = requests.get(
            "https://ak.hypergryph.com/downloads/android_lastest",
            timeout=REQUESTS_TIMEOUT,
            allow_redirects=True,
            stream=True,
        )
        game_link = req.url

        if game_link.endswith(".apk"):
            return game_link

        return None
    except Exception:
        return None


def get_mumu_link():
    try:
        mumu_link = requests.post(
            "https://api.mumuglobal.com/api/v1/download/nx",
            timeout=REQUESTS_TIMEOUT,
            data=[
                ("architecture", "x86_64"),
                ("machine", "{}"),
                ("usage", "1"),
            ],
        ).json()["data"]["mumu"]["link"]

        mumu_link = mumu_link.replace("http://", "https://", 1)
        return mumu_link
    except Exception:
        return None


def get_pc_game_link():
    try:
        obj = requests.get(
            "https://launcher.hypergryph.com/api/game/get_latest?appcode=GzD1CpaWgmSq1wew&platform=Windows&channel=1",
            timeout=REQUESTS_TIMEOUT,
        ).json()

        pc_game_link = "\n".join([i["url"] for i in obj["pkg"]["packs"]])

        return pc_game_link
    except Exception:
        return None


def main():
    game_link = get_game_link()

    if game_link is not None:
        with open(GAME_LINK_FILEPATH, "w", encoding="utf-8") as f:
            f.write(game_link)

    mumu_link = get_mumu_link()

    if mumu_link is not None:
        with open(MUMU_LINK_FILEPATH, "w", encoding="utf-8") as f:
            f.write(mumu_link)

    pc_game_link = get_pc_game_link()

    if pc_game_link is not None:
        with open(PC_GAME_LINK_FILEPATH, "w", encoding="utf-8") as f:
            f.write(pc_game_link)


if __name__ == "__main__":
    main()
