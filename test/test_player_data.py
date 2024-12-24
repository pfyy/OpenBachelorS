import os
import json

from ..src.util.player_data import player_data_template, DeltaJson


def test_player_data_template():
    os.makedirs("cache", exist_ok=True)
    with open("cache/player_data_template.json", "w", encoding="utf-8") as f:
        json.dump(player_data_template.copy(), f, ensure_ascii=False, indent=4)


def test_delta_json():
    delta_json = DeltaJson({}, {})

    delta_json["a"]["b"]["c"] = {}

    delta_json.debug()

    delta_json["a"] = {}

    delta_json.debug()

    print("---")

    delta_json = DeltaJson({}, {})

    delta_json["a"] = {}

    delta_json.debug()

    delta_json["a"]["b"]["c"] = {}

    delta_json.debug()

    print("---")

    delta_json = DeltaJson({}, {})

    delta_json["a"]["b"]["c"] = {}

    delta_json.debug()

    del delta_json["a"]["b"]

    delta_json.debug()

    print("---")

    delta_json = DeltaJson({}, {})

    del delta_json["a"]["b"]

    delta_json.debug()

    delta_json["a"] = {}

    delta_json.debug()

    print("---")

    delta_json = DeltaJson({}, {})

    del delta_json["a"]["b"]

    delta_json.debug()

    delta_json["a"]["b"] = {}

    delta_json.debug()

    print("---")

    delta_json = DeltaJson({}, {})

    del delta_json["a"]["b"]["c"]

    delta_json.debug()

    del delta_json["a"]["b"]

    delta_json.debug()

    print("---")
