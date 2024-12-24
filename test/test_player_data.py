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
    delta_json["a"] = {}
    assert (
        delta_json.modified_json_obj == {"a": {}} and delta_json.deleted_json_obj == {}
    )

    delta_json = DeltaJson({}, {})
    delta_json["a"]["b"]["c"] = {}
    del delta_json["a"]["b"]
    assert delta_json.modified_json_obj == {
        "a": {}
    } and delta_json.deleted_json_obj == {"a": ["b"]}

    delta_json = DeltaJson({}, {})
    del delta_json["a"]["b"]
    delta_json["a"] = {}
    assert (
        delta_json.modified_json_obj == {"a": {}} and delta_json.deleted_json_obj == {}
    )

    delta_json = DeltaJson({}, {})
    del delta_json["a"]["b"]
    delta_json["a"]["b"] = {}
    assert (
        delta_json.modified_json_obj == {"a": {"b": {}}}
        and delta_json.deleted_json_obj == {}
    )

    delta_json = DeltaJson({}, {})
    del delta_json["a"]["b"]["c"]
    del delta_json["a"]["b"]
    assert delta_json.modified_json_obj == {} and delta_json.deleted_json_obj == {
        "a": ["b"]
    }
