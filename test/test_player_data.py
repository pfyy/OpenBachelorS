import os
import json

from ..src.util.player_data import player_data_template


def test_player_data_template():
    os.makedirs("cache", exist_ok=True)
    with open("cache/player_data_template.json", "w", encoding="utf-8") as f:
        json.dump(player_data_template.copy(), f, ensure_ascii=False, indent=4)
