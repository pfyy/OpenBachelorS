import os
import json

import pytest
import orjson

from openbachelors.util.const_json_loader import ConstJson
from openbachelors.const.filepath import TMP_DIRPATH
from openbachelors.util.player_data import (
    DeltaJson,
    OverlayJson,
    player_data_template,
    player_data_decorator,
    PlayerData,
)


def test_writable_overlay_json():
    base_json = ConstJson(
        {
            "k0": {"k1": 0},
            "k2": 0,
        }
    )

    delta_json = DeltaJson()

    overlay_json = OverlayJson(base_json, delta_json)

    overlay_json["k0"] = 1

    assert overlay_json.copy() == {"k2": 0, "k0": 1}
    assert delta_json.modified_dict == {"k0": 1}
    assert delta_json.deleted_dict == {"k0": None}

    overlay_json["k0"] = {}

    assert overlay_json.copy() == {"k2": 0, "k0": {}}
    assert delta_json.modified_dict == {"k0": {}}
    assert delta_json.deleted_dict == {"k0": None}

    overlay_json["k2"] = {
        "k3": {"k4": 2, "k5": {}},
        "k6": {},
    }

    assert overlay_json.copy() == {
        "k0": {},
        "k2": {"k3": {"k4": 2, "k5": {}}, "k6": {}},
    }
    assert delta_json.modified_dict == {
        "k0": {},
        "k2": {"k3": {"k4": 2, "k5": {}}, "k6": {}},
    }
    assert delta_json.deleted_dict == {"k0": None, "k2": None}

    del overlay_json["k2"]["k3"]

    assert overlay_json.copy() == {
        "k0": {},
        "k2": {"k6": {}},
    }
    assert delta_json.modified_dict == {
        "k0": {},
        "k2": {"k6": {}},
    }
    assert delta_json.deleted_dict == {"k0": None, "k2": None}

    overlay_json["k2"]["k6"] = 3

    assert overlay_json.copy() == {
        "k0": {},
        "k2": {"k6": 3},
    }
    assert delta_json.modified_dict == {
        "k0": {},
        "k2": {"k6": 3},
    }
    assert delta_json.deleted_dict == {"k0": None, "k2": None}

    overlay_json["k2"] = {"k7": {"k8": {}}}

    overlay_json["k2"] = {}

    overlay_json["k2"]["k7"] = {}

    assert overlay_json.copy() == {
        "k0": {},
        "k2": {"k6": 3, "k7": {"k8": {}}},
    }
    assert delta_json.modified_dict == {
        "k0": {},
        "k2": {"k6": 3, "k7": {"k8": {}}},
    }
    assert delta_json.deleted_dict == {"k0": None, "k2": None}

    # ---

    base_json = ConstJson(
        {
            "k0": {"k1": 1, "k3": {"k4": 2}},
            "k2": 0,
        }
    )

    delta_json = DeltaJson()

    overlay_json = OverlayJson(base_json, delta_json)

    overlay_json["k0"]["k1"] = {}

    assert overlay_json.copy() == {"k0": {"k3": {"k4": 2}, "k1": {}}, "k2": 0}
    assert delta_json.modified_dict == {"k0": {"k1": {}}}
    assert delta_json.deleted_dict == {"k0": {"k1": None}}

    overlay_json["k0"]["k5"] = 3

    assert overlay_json.copy() == {"k0": {"k3": {"k4": 2}, "k1": {}, "k5": 3}, "k2": 0}
    assert delta_json.modified_dict == {"k0": {"k1": {}, "k5": 3}}
    assert delta_json.deleted_dict == {"k0": {"k1": None}}


def is_empty_dict(target_dict: dict):
    for key, value in target_dict.items():
        if isinstance(value, dict):
            if not is_empty_dict(value):
                return False
        else:
            return False

    return True


def test_nested_overlay_json():
    base_json = ConstJson(
        {
            "k0": {"k1": 0},
            "k2": 1,
        }
    )

    delta_json = DeltaJson()

    overlay_json = OverlayJson(base_json, delta_json)

    delta_json_2 = DeltaJson()
    overlay_json_2 = OverlayJson(overlay_json, delta_json_2)

    overlay_json_2["k3"] = 2

    assert overlay_json_2.copy() == {"k0": {"k1": 0}, "k2": 1, "k3": 2}
    assert delta_json_2.modified_dict == {"k3": 2}
    assert delta_json_2.deleted_dict == {}
    assert is_empty_dict(delta_json.modified_dict)
    assert is_empty_dict(delta_json.deleted_dict)

    overlay_json_2["k0"]["k4"] = 3

    assert overlay_json_2.copy() == {"k0": {"k1": 0, "k4": 3}, "k2": 1, "k3": 2}
    assert delta_json_2.modified_dict == {"k3": 2, "k0": {"k4": 3}}
    assert delta_json_2.deleted_dict == {"k0": {}}
    assert is_empty_dict(delta_json.modified_dict)
    assert is_empty_dict(delta_json.deleted_dict)

    del overlay_json_2["k0"]["k1"]

    assert overlay_json_2.copy() == {"k0": {"k4": 3}, "k2": 1, "k3": 2}
    assert delta_json_2.modified_dict == {"k3": 2, "k0": {"k4": 3}}
    assert delta_json_2.deleted_dict == {"k0": {"k1": None}}
    assert is_empty_dict(delta_json.modified_dict)
    assert is_empty_dict(delta_json.deleted_dict)


def test_player_data_template():
    os.makedirs(TMP_DIRPATH, exist_ok=True)
    with open(
        os.path.join(TMP_DIRPATH, "player_data_template.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(player_data_template.copy(), f, ensure_ascii=False, indent=4)


@pytest.mark.asyncio(loop_scope="session")
async def test_player_data(db_pool_fixture):
    player_data = await PlayerData.create()

    player_data.reset()
    await player_data.save()

    @player_data_decorator
    async def f(player_data):
        player_data["status"]["ap"] = 789
        response = {}
        return response

    response = orjson.loads((await f()).body)

    response.pop("pushMessage", None)

    assert response == {
        "playerDataDelta": {"modified": {"status": {"ap": 789}}, "deleted": {}}
    }

    player_data = await PlayerData.create()

    assert player_data.sav_delta_json.modified_dict == {"status": {"ap": 789}}
    assert player_data.sav_delta_json.deleted_dict == {"status": {"ap": None}}

    assert player_data.sav_pending_delta_json.modified_dict == {}
    assert player_data.sav_pending_delta_json.deleted_dict == {}
