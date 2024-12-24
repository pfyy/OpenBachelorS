import os
import json

from ..src.util.const_json_loader import ConstJson
from ..src.util.player_data import (
    player_data_template,
    DeltaJson,
    JsonWithDelta,
    PlayerData,
    player_data_decorator,
)


def test_player_data_template():
    os.makedirs("cache", exist_ok=True)
    with open("cache/player_data_template.json", "w", encoding="utf-8") as f:
        json.dump(player_data_template.copy(), f, ensure_ascii=False, indent=4)


def test_delta_json():
    delta_json = DeltaJson({}, {})
    delta_json["a"]["b"]["c"] = {}
    assert (
        delta_json.modified_json_obj == {"a": {"b": {"c": {}}}}
        and delta_json.deleted_json_obj == {}
    )

    delta_json = DeltaJson({}, {})
    del delta_json["a"]["b"]["c"]
    assert delta_json.modified_json_obj == {} and delta_json.deleted_json_obj == {
        "a": {"b": ["c"]}
    }

    delta_json = DeltaJson({}, {})
    delta_json["a"]["b"]["c"] = {}
    delta_json["a"] = {}
    assert (
        delta_json.modified_json_obj == {"a": {}} and delta_json.deleted_json_obj == {}
    )

    delta_json = DeltaJson({}, {})
    delta_json["a"]["b"]["c"] = {}
    delta_json["a"]["b"]["d"] = {}
    assert (
        delta_json.modified_json_obj == {"a": {"b": {"c": {}, "d": {}}}}
        and delta_json.deleted_json_obj == {}
    )

    delta_json = DeltaJson({}, {})
    delta_json["a"]["b"]["c"] = {}
    del delta_json["a"]["b"]
    assert delta_json.modified_json_obj == {
        "a": {}
    } and delta_json.deleted_json_obj == {"a": ["b"]}

    delta_json = DeltaJson({}, {})
    delta_json["a"]["b"]["c"] = {}
    del delta_json["a"]["b"]["d"]
    assert delta_json.modified_json_obj == {
        "a": {"b": {"c": {}}}
    } and delta_json.deleted_json_obj == {"a": {"b": ["d"]}}

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
    del delta_json["a"]["b"]
    delta_json["a"]["c"] = {}
    assert delta_json.modified_json_obj == {
        "a": {"c": {}}
    } and delta_json.deleted_json_obj == {"a": ["b"]}

    delta_json = DeltaJson({}, {})
    del delta_json["a"]["b"]["c"]
    del delta_json["a"]["b"]
    assert delta_json.modified_json_obj == {} and delta_json.deleted_json_obj == {
        "a": ["b"]
    }


def test_json_with_delta():
    const_json = ConstJson(
        {"a": {"b": {"d": "e"}, "c": 123, "f": {"g": "h"}}, "u": 234}
    )
    delta_json = DeltaJson({}, {})
    json_with_delta = JsonWithDelta(const_json, delta_json)

    json_with_delta["a"]["b"] = 456

    del json_with_delta["a"]["f"]["g"]

    json_with_delta["a"]["c"] = {"x": {"y": "z"}}

    del json_with_delta["a"]["c"]["x"]["y"]

    assert json_with_delta.copy() == {
        "a": {"b": 456, "c": {"x": {}}, "f": {}},
        "u": 234,
    }


def test_json_with_delta_iter():
    const_json = ConstJson(
        {"a": {"b": {"d": "e"}, "c": 123, "f": {"g": "h"}}, "u": 234}
    )
    delta_json = DeltaJson({}, {})
    json_with_delta = JsonWithDelta(const_json, delta_json)

    json_with_delta["a"]["b"] = 456

    del json_with_delta["a"]["f"]["g"]

    json_with_delta["a"]["c"] = {"x": {"y": "z"}}

    del json_with_delta["a"]["c"]["x"]["y"]

    assert json_with_delta.copy() == {
        "a": {"b": 456, "c": {"x": {}}, "f": {}},
        "u": 234,
    }

    assert set([i[0] for i in json_with_delta]) == set(["a", "u"])


def test_player_data():
    player_data = PlayerData()

    player_data.reset()

    player_data["status"]["nickName"] = "SomeRandomName"

    delta_response = player_data.build_delta_response()
    player_data.save()


def test_player_data_decorator():
    @player_data_decorator
    def f(player_data):
        player_data["status"]["ap"] = 888
        return {}

    response = f()

    assert response["playerDataDelta"]["modified"]["status"]["ap"] == 888
