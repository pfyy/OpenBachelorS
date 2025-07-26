from enum import Enum
from copy import deepcopy

from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import (
    CONFIG_JSON,
    VERSION_JSON,
    ROGUELIKE_TOPIC_TABLE,
    CHARACTER_TABLE,
    RLV2_DATA,
)
from ..util.const_json_loader import const_json_loader, ConstJson
from ..util.player_data import player_data_decorator, char_id_lst
from ..util.helper import (
    get_char_num_id,
)
from ..util.battle_log_logger import log_battle_log_if_necessary

bp_rlv2 = Blueprint("bp_rlv2", __name__)

profession_lst = ConstJson(
    [
        "PIONEER",
        "WARRIOR",
        "TANK",
        "SNIPER",
        "CASTER",
        "MEDIC",
        "SUPPORT",
        "SPECIAL",
    ]
)


def build_profession_char_id_lst_dict():
    profession_char_id_lst_dict = {}

    for i, profession in profession_lst:
        profession_char_id_lst_dict[profession] = []

    character_table = const_json_loader[CHARACTER_TABLE]

    for i, char_id in char_id_lst:
        profession = character_table[char_id]["profession"]

        profession_char_id_lst_dict[profession].append(char_id)

    return ConstJson(profession_char_id_lst_dict)


profession_char_id_lst_dict = build_profession_char_id_lst_dict()


class Rlv2BasicManager:
    def __init__(self, player_data, theme_id, request_json, response):
        self.player_data = player_data
        self.theme_id = theme_id
        self.request_json = request_json
        self.response = response

    def rlv2_createGame(self):
        mode = self.request_json["mode"]
        mode_grade = self.request_json["modeGrade"]

        roguelike_topic_table = const_json_loader[ROGUELIKE_TOPIC_TABLE]

        init_idx = 0
        for i, init_obj in roguelike_topic_table["details"][self.theme_id]["init"]:
            if init_obj["modeId"] == mode and init_obj["modeGrade"] == mode_grade:
                init_idx = i
                break

        init_obj = roguelike_topic_table["details"][self.theme_id]["init"][init_idx]

        init_band_relic_lst = init_obj["initialBandRelic"].copy()
        init_band_relic_dict = {}

        for i, init_band_relic in enumerate(init_band_relic_lst):
            init_band_relic_dict[str(i)] = {"id": init_band_relic, "count": 1}

        init_recruit_group_lst = init_obj["initialRecruitGroup"].copy()

        for ending_id, ending_obj in roguelike_topic_table["details"][self.theme_id][
            "endings"
        ]:
            break

        rlv2_obj = {
            "player": {
                "state": "INIT",
                "property": {
                    "exp": 0,
                    "level": 10,
                    "maxLevel": 10,
                    "hp": {"current": 1, "max": 1},
                    "gold": 99999,
                    "shield": 99999,
                    "capacity": 13,
                    "population": {"cost": 0, "max": 99999},
                    "conPerfectBattle": 0,
                    "hpShowState": "NORMAL",
                },
                "cursor": {"zone": 0, "position": null},
                "trace": [],
                "pending": [
                    {
                        "index": "e_0",
                        "type": "GAME_INIT_RELIC",
                        "content": {
                            "initRelic": {
                                "step": [1, 3],
                                "items": init_band_relic_dict,
                            }
                        },
                    },
                    {
                        "index": "e_1",
                        "type": "GAME_INIT_RECRUIT_SET",
                        "content": {
                            "initRecruitSet": {
                                "step": [2, 3],
                                "option": init_recruit_group_lst,
                            }
                        },
                    },
                    {
                        "index": "e_2",
                        "type": "GAME_INIT_RECRUIT",
                        "content": {
                            "initRecruit": {
                                "step": [3, 3],
                                "tickets": [],
                                "showChar": [],
                                "team": null,
                            }
                        },
                    },
                ],
                "status": {"bankPut": 0},
                "toEnding": ending_id,
                "chgEnding": false,
            },
            "map": {"zones": {}},
            "troop": {
                "chars": {},
                "expedition": [],
                "expeditionDetails": {},
                "expeditionReturn": null,
                "hasExpeditionReturn": false,
            },
            "inventory": {
                "relic": {},
                "recruit": {},
                "trap": null,
                "consumable": {},
                "exploreTool": {},
            },
            "game": {
                "mode": mode,
                "predefined": null,
                "outer": {"support": false},
                "start": 1700000000,
                "modeGrade": mode_grade,
                "equivalentGrade": mode_grade,
            },
            "buff": {"tmpHP": 99999, "capsule": null, "squadBuff": []},
            "record": {"brief": null},
            "module": {},
        }

        self.player_data["rlv2"]["current"] = rlv2_obj

    def rlv2_giveUpGame(self):
        self.player_data["rlv2"]["current"] = {
            "player": null,
            "map": null,
            "troop": null,
            "inventory": null,
            "game": null,
            "buff": null,
            "module": null,
            "record": null,
        }

    def rlv2_chooseInitialRelic(self):
        init_band_relic_idx = self.request_json["select"]

        pending_lst = self.player_data["rlv2"]["current"]["player"]["pending"].copy()
        init_band_relic = pending_lst[0]["content"]["initRelic"]["items"][
            init_band_relic_idx
        ]["id"]
        self.player_data["rlv2"]["current"]["inventory"]["relic"]["r_0"] = {
            "index": "r_0",
            "id": init_band_relic,
            "count": 1,
            "ts": 1700000000,
        }

        pending_lst.pop(0)
        self.player_data["rlv2"]["current"]["player"]["pending"] = pending_lst

    def rlv2_chooseInitialRecruitSet(self):
        init_recruit_group = self.request_json["select"]

        pending_lst = self.player_data["rlv2"]["current"]["player"]["pending"].copy()

        pending_lst.pop(0)
        self.player_data["rlv2"]["current"]["player"]["pending"] = pending_lst

    class NodeType(Enum):
        BATTLE = 1
        ELITE_BATTLE = 2
        BOSS_BATTLE = 4
        SHOP = 8

    theme_id_node_type_dict = ConstJson(
        {
            "rogue_1": {
                NodeType.BATTLE: 1,
                NodeType.ELITE_BATTLE: 2,
                NodeType.BOSS_BATTLE: 4,
                NodeType.SHOP: 8,
            },
            "rogue_2": {
                NodeType.BATTLE: 1,
                NodeType.ELITE_BATTLE: 2,
                NodeType.BOSS_BATTLE: 4,
                NodeType.SHOP: 4096,
            },
            "rogue_3": {
                NodeType.BATTLE: 1,
                NodeType.ELITE_BATTLE: 2,
                NodeType.BOSS_BATTLE: 4,
                NodeType.SHOP: 4096,
            },
            "rogue_4": {
                NodeType.BATTLE: 1,
                NodeType.ELITE_BATTLE: 2,
                NodeType.BOSS_BATTLE: 4,
                NodeType.SHOP: 4096,
            },
        }
    )

    def get_node_type_int(self, theme_id, node_type):
        if theme_id not in self.theme_id_node_type_dict:
            theme_id = "rogue_4"

        return self.theme_id_node_type_dict[theme_id][node_type]

    MAX_NODE_POS_X = 10
    MAX_NODE_POS_Y = 4

    def get_zone_idx(self, zone_num_idx):
        return 1000 + zone_num_idx

    def get_node_idx(self, node_pos_x, node_pos_y):
        if not node_pos_x:
            return f"{node_pos_y}"
        return f"{node_pos_x}0{node_pos_y}"

    def create_simple_zone_obj(self, zone_num_idx):
        zone_obj = {
            "id": f"zone_{zone_num_idx + 1}",
            "index": self.get_zone_idx(zone_num_idx),
            "nodes": {},
            "variation": [],
        }

        node_type_int = self.get_node_type_int(self.theme_id, self.NodeType.SHOP)

        first_node_pos_x, first_node_pos_y = 0, 0
        first_node_idx = self.get_node_idx(first_node_pos_x, first_node_pos_y)
        first_node_obj = {
            "index": first_node_idx,
            "pos": {"x": first_node_pos_x, "y": first_node_pos_y},
            "next": [],
            "type": node_type_int,
        }
        zone_obj["nodes"][first_node_idx] = first_node_obj

        node_pos_x, node_pos_y = 1, 0
        node_idx = self.get_node_idx(node_pos_x, node_pos_y)
        node_obj = {
            "index": node_idx,
            "pos": {"x": node_pos_x, "y": node_pos_y},
            "next": [],
            "type": node_type_int,
        }
        zone_obj["nodes"][node_idx] = node_obj

        zone_obj["nodes"][first_node_idx]["next"].append(
            {"x": node_pos_x, "y": node_pos_y}
        )

        return zone_obj

    def add_zone_obj_last_node(self, zone_obj, last_node_pos_x):
        node_type_int = self.get_node_type_int(self.theme_id, self.NodeType.SHOP)

        last_node_pos_y = 0
        last_node_idx = self.get_node_idx(last_node_pos_x, last_node_pos_y)
        last_node_obj = {
            "index": last_node_idx,
            "pos": {"x": last_node_pos_x, "y": last_node_pos_y},
            "next": [],
            "type": node_type_int,
            "zone_end": true,
        }
        zone_obj["nodes"][last_node_idx] = last_node_obj

        first_node_pos_x, first_node_pos_y = 0, 0
        first_node_idx = self.get_node_idx(first_node_pos_x, first_node_pos_y)
        zone_obj["nodes"][first_node_idx]["next"].append(
            {"x": last_node_pos_x, "y": last_node_pos_y}
        )

    def create_simple_map(self):
        zone_dict = {}

        first_node_pos_x, first_node_pos_y = 0, 0
        first_node_idx = self.get_node_idx(first_node_pos_x, first_node_pos_y)

        zone_num_idx = 0
        zone_idx = self.get_zone_idx(zone_num_idx)
        zone_obj = self.create_simple_zone_obj(zone_num_idx)

        node_pos_x, node_pos_y = 1, 1

        roguelike_topic_table = const_json_loader[ROGUELIKE_TOPIC_TABLE]

        for stage_id, stage_obj in roguelike_topic_table["details"][self.theme_id][
            "stages"
        ]:
            if node_pos_y >= self.MAX_NODE_POS_Y:
                node_pos_y = 0
                node_pos_x += 1
            if node_pos_x >= self.MAX_NODE_POS_X - 1:
                self.add_zone_obj_last_node(zone_obj, node_pos_x)
                zone_dict[str(zone_idx)] = zone_obj

                zone_num_idx += 1
                zone_idx = self.get_zone_idx(zone_num_idx)
                zone_obj = self.create_simple_zone_obj(zone_num_idx)

                node_pos_x, node_pos_y = 1, 1

            node_type = self.NodeType.BATTLE
            if stage_obj["isElite"]:
                node_type = self.NodeType.ELITE_BATTLE
            if stage_obj["isBoss"]:
                node_type = self.NodeType.BOSS_BATTLE

            node_type_int = self.get_node_type_int(self.theme_id, node_type)

            node_idx = self.get_node_idx(node_pos_x, node_pos_y)
            node_obj = {
                "index": node_idx,
                "pos": {"x": node_pos_x, "y": node_pos_y},
                "next": [],
                "type": node_type_int,
                "stage": stage_id,
            }
            zone_obj["nodes"][node_idx] = node_obj

            zone_obj["nodes"][first_node_idx]["next"].append(
                {"x": node_pos_x, "y": node_pos_y}
            )

            node_pos_y += 1

        self.add_zone_obj_last_node(zone_obj, node_pos_x + 1)
        zone_dict[str(zone_idx)] = zone_obj

        return zone_dict

    def rlv2_finishEvent(self):
        self.player_data["rlv2"]["current"]["player"]["state"] = "WAIT_MOVE"
        self.player_data["rlv2"]["current"]["player"]["pending"] = []

        self.player_data["rlv2"]["current"]["map"]["zones"] = self.create_simple_map()
        self.player_data["rlv2"]["current"]["player"]["cursor"]["zone"] = (
            self.get_zone_idx(0)
        )

    def get_good_lst(self):
        good_lst = []
        good_idx = 0

        roguelike_topic_table = const_json_loader[ROGUELIKE_TOPIC_TABLE]

        gold_id = roguelike_topic_table["details"][self.theme_id]["gameConst"][
            "goldItemId"
        ]

        for i, profession in profession_lst:
            profession = profession.lower()

            item_id_lst = [
                f"{self.theme_id}_recruit_ticket_{profession}",
                f"{self.theme_id}_recruit_ticket_{profession}_sp",
            ]

            for item_id in item_id_lst:
                good_lst.append(
                    {
                        "index": str(good_idx),
                        "itemId": item_id,
                        "count": 1,
                        "priceId": gold_id,
                        "priceCount": 0,
                        "origCost": 0,
                        "displayPriceChg": false,
                        "_retainDiscount": 1,
                    }
                )

                good_idx += 1

        for item_id, item_obj in roguelike_topic_table["details"][self.theme_id][
            "items"
        ]:
            item_type = item_obj["type"]
            if item_type != "RELIC" and item_type != "ACTIVE_TOOL":
                continue

            good_lst.append(
                {
                    "index": str(good_idx),
                    "itemId": item_id,
                    "count": 1,
                    "priceId": gold_id,
                    "priceCount": 0,
                    "origCost": 0,
                    "displayPriceChg": false,
                    "_retainDiscount": 1,
                }
            )

            good_idx += 1

        return good_lst

    def rlv2_moveTo(self):
        cursor_pos = self.request_json["to"]

        good_lst = self.get_good_lst()

        self.player_data["rlv2"]["current"]["player"]["state"] = "PENDING"
        self.player_data["rlv2"]["current"]["player"]["cursor"]["position"] = cursor_pos
        self.player_data["rlv2"]["current"]["player"]["pending"] = [
            {
                "index": "e_3",
                "type": "SHOP",
                "content": {
                    "shop": {
                        "bank": {
                            "open": true,
                            "canPut": true,
                            "canWithdraw": true,
                            "withdraw": 0,
                            "cost": 1,
                        },
                        "id": "zone_1_shop",
                        "goods": good_lst,
                        "_done": false,
                    }
                },
            }
        ]

    def leave_node(self):
        zone_idx = self.player_data["rlv2"]["current"]["player"]["cursor"]["zone"]
        cursor_pos = self.player_data["rlv2"]["current"]["player"]["cursor"][
            "position"
        ].copy()

        node_pos_x, node_pos_y = cursor_pos["x"], cursor_pos["y"]
        node_idx = self.get_node_idx(node_pos_x, node_pos_y)

        if (
            "zone_end"
            in self.player_data["rlv2"]["current"]["map"]["zones"][str(zone_idx)][
                "nodes"
            ][node_idx]
        ):
            zone_idx += 1
            if str(zone_idx) not in self.player_data["rlv2"]["current"]["map"]["zones"]:
                zone_idx = self.get_zone_idx(0)
            self.player_data["rlv2"]["current"]["player"]["cursor"]["zone"] = zone_idx
            self.player_data["rlv2"]["current"]["player"]["cursor"]["position"] = null
        else:
            self.player_data["rlv2"]["current"]["player"]["cursor"]["position"] = {
                "x": 0,
                "y": 0,
            }

    def get_next_relic_id(self):
        relic_idx = 0
        while True:
            relic_id = f"r_{relic_idx}"
            if (
                relic_id
                not in self.player_data["rlv2"]["current"]["inventory"]["relic"]
            ):
                break
            relic_idx += 1
        return relic_id

    def get_next_ticket_id(self):
        ticket_idx = 1
        while True:
            ticket_id = f"t_{ticket_idx}"
            if (
                ticket_id
                not in self.player_data["rlv2"]["current"]["inventory"]["recruit"]
            ):
                break
            ticket_idx += 1
        return ticket_id

    def get_ticket_info(self, ticket_item_id):
        sp_suffix = "_sp"
        if ticket_item_id.endswith(sp_suffix):
            upgrade_limited = False
            ticket_item_id = ticket_item_id[: -len(sp_suffix)]
        else:
            upgrade_limited = True
        profession = ticket_item_id.rpartition("_")[-1].upper()
        return profession, upgrade_limited

    def get_degraded_char_max_level(self, char_id):
        character_table = const_json_loader[CHARACTER_TABLE]

        char_rarity = character_table[char_id]["rarity"]

        if char_rarity == "TIER_6":
            return 80

        if char_rarity == "TIER_5":
            return 70

        return 60

    def degrade_char_obj_if_necessary(self, char_obj):
        if char_obj["evolvePhase"] < 2:
            return

        char_obj["evolvePhase"] = 1

        char_id = char_obj["charId"]
        degraded_char_max_level = self.get_degraded_char_max_level(char_id)
        char_obj["level"] = degraded_char_max_level

        if "tmpl" in char_obj:
            for tmpl_id in char_obj["tmpl"]:
                tmpl_obj = char_obj["tmpl"][tmpl_id]
                if tmpl_obj["defaultSkillIndex"] == 2:
                    tmpl_obj["defaultSkillIndex"] = 1
                if len(tmpl_obj["skills"]) == 3:
                    tmpl_obj["skills"][2]["unlock"] = 0
                for skill_obj in tmpl_obj["skills"]:
                    skill_obj["specializeLevel"] = 0
        else:
            if char_obj["defaultSkillIndex"] == 2:
                char_obj["defaultSkillIndex"] = 1
            if len(char_obj["skills"]) == 3:
                char_obj["skills"][2]["unlock"] = 0
            for skill_obj in char_obj["skills"]:
                skill_obj["specializeLevel"] = 0

    def get_ticket_char_obj_lst(self, ticket_item_id):
        profession, upgrade_limited = self.get_ticket_info(ticket_item_id)
        ticket_char_obj_lst = []

        char_idx = 0

        for i, char_id in profession_char_id_lst_dict[profession]:
            char_num_id = get_char_num_id(char_id)
            char_obj = self.player_data["troop"]["chars"][str(char_num_id)].copy()

            if upgrade_limited:
                self.degrade_char_obj_if_necessary(char_obj)

            char_obj.update(
                {
                    "type": "NORMAL",
                    "upgradeLimited": upgrade_limited,
                    "upgradePhase": int(not upgrade_limited),
                    "isUpgrade": false,
                    "isCure": false,
                    "population": 0,
                    "charBuff": [],
                    "troopInstId": "0",
                }
            )

            if "tmpl" in char_obj:
                for tmpl_id in char_obj["tmpl"]:
                    dup_char_obj = deepcopy(char_obj)
                    dup_char_obj["currentTmpl"] = tmpl_id

                    dup_char_obj["instId"] = str(char_idx)
                    ticket_char_obj_lst.append(dup_char_obj)
                    char_idx += 1
            else:
                char_obj["instId"] = str(char_idx)
                ticket_char_obj_lst.append(char_obj)
                char_idx += 1

        return ticket_char_obj_lst

    def rlv2_shopAction(self):
        if self.request_json["leave"]:
            self.player_data["rlv2"]["current"]["player"]["state"] = "WAIT_MOVE"
            self.player_data["rlv2"]["current"]["player"]["pending"] = []

            self.leave_node()
            return

        roguelike_topic_table = const_json_loader[ROGUELIKE_TOPIC_TABLE]

        for good_idx in self.request_json["buy"]:
            good_idx = int(good_idx)

            good_id = self.player_data["rlv2"]["current"]["player"]["pending"][0][
                "content"
            ]["shop"]["goods"][good_idx]["itemId"]

            good_type = roguelike_topic_table["details"][self.theme_id]["items"][
                good_id
            ]["type"]
            if good_type == "RECRUIT_TICKET":
                ticket_id = self.get_next_ticket_id()

                ticket_char_obj_lst = self.get_ticket_char_obj_lst(good_id)

                self.player_data["rlv2"]["current"]["inventory"]["recruit"][
                    ticket_id
                ] = {
                    "index": ticket_id,
                    "id": good_id,
                    "state": 1,
                    "list": ticket_char_obj_lst,
                    "result": null,
                    "ts": 1700000000,
                    "from": "shop",
                    "mustExtra": 0,
                    "needAssist": false,
                }

                pending_lst = self.player_data["rlv2"]["current"]["player"][
                    "pending"
                ].copy()

                pending_lst.insert(
                    0,
                    {
                        "index": "e_6",
                        "type": "RECRUIT",
                        "content": {"recruit": {"ticket": ticket_id}},
                    },
                )

                self.player_data["rlv2"]["current"]["player"]["pending"] = pending_lst
            elif good_type == "RELIC":
                relic_id = self.get_next_relic_id()
                self.player_data["rlv2"]["current"]["inventory"]["relic"][relic_id] = {
                    "index": relic_id,
                    "id": good_id,
                    "count": 1,
                    "ts": 1700000000,
                }

            elif good_type == "ACTIVE_TOOL":
                self.player_data["rlv2"]["current"]["inventory"]["trap"] = {
                    "index": good_id,
                    "id": good_id,
                    "count": 1,
                    "ts": 1700000000,
                }

    def get_floor_difficulty(self, mode, mode_grade):
        roguelike_topic_table = const_json_loader[ROGUELIKE_TOPIC_TABLE]

        floor_difficulty = 0

        for i, difficulty_obj in roguelike_topic_table["details"][self.theme_id][
            "difficulties"
        ]:
            if (
                difficulty_obj["modeDifficulty"] == mode
                and difficulty_obj["grade"] == mode_grade
            ):
                floor_difficulty = difficulty_obj["bossValue"]
                break

        return floor_difficulty

    def get_stage_floor(self, stage_id):
        rlv2_data = const_json_loader[RLV2_DATA]

        if stage_id in rlv2_data["stage_floor"]:
            stage_floor = rlv2_data["stage_floor"][stage_id]
            return stage_floor

        return 5

    def get_stage_buff_lst(self, floor_difficulty):
        stage_id = self.request_json["stageId"]

        stage_floor = self.get_stage_floor(stage_id)

        stage_buff_lst = []

        floor_difficulty_rate = 1 + 0.01 * floor_difficulty

        stage_buff_lst += [
            {
                "key": "zone_into_buff",
                "blackboard": [
                    {"key": "buff", "valueStr": "global_buff_normal"},
                    {"key": "key", "valueStr": "enemy_atk_down"},
                    {"key": "atk", "value": floor_difficulty_rate},
                ],
            },
            {
                "key": "zone_into_buff",
                "blackboard": [
                    {"key": "buff", "valueStr": "global_buff_normal"},
                    {"key": "key", "valueStr": "enemy_max_hp_down"},
                    {"key": "max_hp", "value": floor_difficulty_rate},
                ],
            },
        ]

        for i in range(stage_floor):
            stage_buff_lst += [
                {
                    "key": "global_buff_normal",
                    "blackboard": [
                        {"key": "key", "valueStr": "enemy_atk_down"},
                        {"key": "atk", "value": floor_difficulty_rate},
                    ],
                },
                {
                    "key": "global_buff_normal",
                    "blackboard": [
                        {"key": "key", "valueStr": "enemy_max_hp_down"},
                        {"key": "max_hp", "value": floor_difficulty_rate},
                    ],
                },
            ]
        return stage_buff_lst

    def get_difficulty_buff_lst(self, mode_grade):
        difficulty_buff_lst = []

        rlv2_data = const_json_loader[RLV2_DATA]

        if self.theme_id in rlv2_data["difficulty_buff_lst"]:
            while (
                str(mode_grade) not in rlv2_data["difficulty_buff_lst"][self.theme_id]
            ):
                mode_grade -= 1
            for i, child_mode_grade in rlv2_data["difficulty_buff_lst"][self.theme_id][
                str(mode_grade)
            ]["child_mode_grade_lst"]:
                difficulty_buff_lst += rlv2_data["difficulty_buff_lst"][self.theme_id][
                    str(child_mode_grade)
                ]["buff_lst"].copy()
            difficulty_buff_lst += rlv2_data["difficulty_buff_lst"][self.theme_id][
                str(mode_grade)
            ]["buff_lst"].copy()

        return difficulty_buff_lst

    def get_unkeep_buff(self):
        unkeep_buff = []

        mode = self.player_data["rlv2"]["current"]["game"]["mode"]
        mode_grade = self.player_data["rlv2"]["current"]["game"]["modeGrade"]

        roguelike_topic_table = const_json_loader[ROGUELIKE_TOPIC_TABLE]

        rlv2_data = const_json_loader[RLV2_DATA]

        if self.theme_id in rlv2_data["init_buff_lst"]:
            init_buff_lst = rlv2_data["init_buff_lst"][self.theme_id].copy()
            unkeep_buff += init_buff_lst

        if self.theme_id in rlv2_data["conditional_init_buff_lst"]:
            for src_mode_grade, src_obj in rlv2_data["conditional_init_buff_lst"][
                self.theme_id
            ]:
                if mode_grade >= int(src_mode_grade):
                    conditional_init_buff_lst = src_obj.copy()
                    unkeep_buff += conditional_init_buff_lst

        if self.player_data["rlv2"]["current"]["inventory"]["trap"] is not None:
            active_tool_id = self.player_data["rlv2"]["current"]["inventory"]["trap"][
                "id"
            ]
            active_tool_buff_lst = roguelike_topic_table["details"][self.theme_id][
                "relics"
            ][active_tool_id]["buffs"].copy()
            unkeep_buff += active_tool_buff_lst

        difficulty_buff_lst = self.get_difficulty_buff_lst(mode_grade)
        unkeep_buff += difficulty_buff_lst

        floor_difficulty = self.get_floor_difficulty(mode, mode_grade)
        if floor_difficulty:
            stage_buff_lst = self.get_stage_buff_lst(floor_difficulty)
            unkeep_buff += stage_buff_lst

        return unkeep_buff

    def rlv2_moveAndBattleStart(self):
        self.response.update(
            {
                "battleId": "00000000-0000-0000-0000-000000000000",
            }
        )

        cursor_pos = self.request_json["to"]

        roguelike_topic_table = const_json_loader[ROGUELIKE_TOPIC_TABLE]

        box_info = {}
        bad_box_id = roguelike_topic_table["details"][self.theme_id]["gameConst"][
            "badBoxTrapId"
        ]
        if bad_box_id is not None:
            box_info[bad_box_id] = 999

        dice_roll_lst = [12] * 99

        unkeep_buff = self.get_unkeep_buff()

        self.player_data["rlv2"]["current"]["player"]["state"] = "PENDING"
        self.player_data["rlv2"]["current"]["player"]["cursor"]["position"] = cursor_pos
        self.player_data["rlv2"]["current"]["player"]["pending"] = [
            {
                "index": "e_4",
                "type": "BATTLE",
                "content": {
                    "battle": {
                        "state": 1,
                        "chestCnt": 999,
                        "goldTrapCnt": 999,
                        "diceRoll": dice_roll_lst,
                        "boxInfo": box_info,
                        "tmpChar": [],
                        "sanity": 0,
                        "unKeepBuff": unkeep_buff,
                        "seed": 0,
                        "enemyHpInfo": {},
                    }
                },
            }
        ]

    def rlv2_battleFinish(self):
        self.player_data["rlv2"]["current"]["player"]["pending"] = [
            {
                "index": "e_5",
                "type": "BATTLE_REWARD",
                "content": {
                    "battleReward": {
                        "earn": {
                            "damage": 0,
                            "hp": 0,
                            "shield": 0,
                            "exp": 0,
                            "populationMax": 0,
                            "squadCapacity": 0,
                            "maxHpUp": 0,
                        },
                        "rewards": [],
                        "show": "1",
                        "state": 0,
                        "isPerfect": 1,
                    }
                },
            }
        ]

    def rlv2_finishBattleReward(self):
        self.player_data["rlv2"]["current"]["player"]["state"] = "WAIT_MOVE"
        self.player_data["rlv2"]["current"]["player"]["pending"] = []

        self.leave_node()

    def get_next_char_inst_id(self):
        char_inst_id = 1

        while True:
            if (
                str(char_inst_id)
                not in self.player_data["rlv2"]["current"]["troop"]["chars"]
            ):
                break
            char_inst_id += 1

        return str(char_inst_id)

    def rlv2_recruitChar(self):
        ticket_id = self.request_json["ticketIndex"]
        char_idx = int(self.request_json["optionId"])

        char_obj = self.player_data["rlv2"]["current"]["inventory"]["recruit"][
            ticket_id
        ]["list"][char_idx].copy()

        self.player_data["rlv2"]["current"]["inventory"]["recruit"][ticket_id][
            "state"
        ] = 2
        self.player_data["rlv2"]["current"]["inventory"]["recruit"][ticket_id][
            "list"
        ] = []
        self.player_data["rlv2"]["current"]["inventory"]["recruit"][ticket_id][
            "result"
        ] = char_obj

        char_inst_id = self.get_next_char_inst_id()
        self.player_data["rlv2"]["current"]["troop"]["chars"][char_inst_id] = char_obj
        self.player_data["rlv2"]["current"]["troop"]["chars"][char_inst_id][
            "instId"
        ] = char_inst_id

        pending_lst = self.player_data["rlv2"]["current"]["player"]["pending"].copy()
        pending_lst.pop(0)
        self.player_data["rlv2"]["current"]["player"]["pending"] = pending_lst

        self.response.update({"chars": [char_obj]})

    def rlv2_closeRecruitTicket(self):
        ticket_id = self.request_json["id"]

        self.player_data["rlv2"]["current"]["inventory"]["recruit"][ticket_id][
            "state"
        ] = 2
        self.player_data["rlv2"]["current"]["inventory"]["recruit"][ticket_id][
            "list"
        ] = []

        pending_lst = self.player_data["rlv2"]["current"]["player"]["pending"].copy()
        pending_lst.pop(0)
        self.player_data["rlv2"]["current"]["player"]["pending"] = pending_lst


class Rlv2Theme1BasicManager(Rlv2BasicManager):
    def get_floor_difficulty(self, mode, mode_grade):
        return 0


class Rlv2Theme2BasicManager(Rlv2BasicManager):
    def get_unkeep_buff(self):
        unkeep_buff = super().get_unkeep_buff()

        unkeep_buff.append(
            {
                "key": "misc_insert_token_card",
                "blackboard": [
                    {"key": "token_key", "valueStr": "trap_089_dice3"},
                    {"key": "level", "value": 1},
                    {"key": "skill", "value": 0},
                    {"key": "cnt", "value": 99},
                ],
            }
        )

        return unkeep_buff

    def get_stage_buff_lst(self, floor_difficulty):
        stage_id = self.request_json["stageId"]

        stage_floor = self.get_stage_floor(stage_id)

        stage_buff_lst = []

        if floor_difficulty == 16:
            atk_floor_difficulty_rate = 1 + 0.01 * 20
            hp_floor_difficulty_rate = 1 + 0.01 * 20
        elif floor_difficulty == 17:
            atk_floor_difficulty_rate = 1 + 0.01 * 20
            hp_floor_difficulty_rate = 1 + 0.01 * 25
        elif floor_difficulty == 18:
            atk_floor_difficulty_rate = 1 + 0.01 * 20
            hp_floor_difficulty_rate = 1 + 0.01 * 30
        else:
            atk_floor_difficulty_rate = 1 + 0.01 * floor_difficulty
            hp_floor_difficulty_rate = 1 + 0.01 * floor_difficulty

        stage_buff_lst += [
            {
                "key": "zone_into_buff",
                "blackboard": [
                    {"key": "buff", "valueStr": "global_buff_normal"},
                    {"key": "key", "valueStr": "enemy_atk_down"},
                    {"key": "atk", "value": atk_floor_difficulty_rate},
                ],
            },
            {
                "key": "zone_into_buff",
                "blackboard": [
                    {"key": "buff", "valueStr": "global_buff_normal"},
                    {"key": "key", "valueStr": "enemy_max_hp_down"},
                    {"key": "max_hp", "value": hp_floor_difficulty_rate},
                ],
            },
        ]

        for i in range(stage_floor):
            stage_buff_lst += [
                {
                    "key": "global_buff_normal",
                    "blackboard": [
                        {"key": "key", "valueStr": "enemy_atk_down"},
                        {"key": "atk", "value": atk_floor_difficulty_rate},
                    ],
                },
                {
                    "key": "global_buff_normal",
                    "blackboard": [
                        {"key": "key", "valueStr": "enemy_max_hp_down"},
                        {"key": "max_hp", "value": hp_floor_difficulty_rate},
                    ],
                },
            ]
        return stage_buff_lst


class Rlv2Theme4BasicManager(Rlv2BasicManager):
    def get_stage_buff_lst(self, floor_difficulty):
        stage_id = self.request_json["stageId"]

        stage_floor = self.get_stage_floor(stage_id)

        stage_buff_lst = []

        floor_difficulty_rate = 1 + 0.01 * floor_difficulty

        stage_buff_lst += [
            {
                "key": "zone_into_buff",
                "blackboard": [
                    {"key": "buff", "valueStr": "global_buff_normal"},
                    {"key": "key", "valueStr": "enemy_atk_down"},
                    {"key": "atk", "value": floor_difficulty_rate},
                ],
            },
            {
                "key": "zone_into_buff",
                "blackboard": [
                    {"key": "buff", "valueStr": "global_buff_normal"},
                    {"key": "key", "valueStr": "enemy_max_hp_down"},
                    {"key": "max_hp", "value": floor_difficulty_rate},
                    {
                        "key": "selector.enemy_exclude",
                        "valueStr": "enemy_1196_msfyin_2|enemy_1200_msfjin_2|enemy_1202_msfzhi_2|enemy_1208_msfji_2|enemy_1210_msfden_2|enemy_1198_msfshu_2",
                    },
                    {"key": "selector.profession", "valueStr": "none"},
                ],
            },
        ]

        for i in range(stage_floor):
            stage_buff_lst += [
                {
                    "key": "global_buff_normal",
                    "blackboard": [
                        {"key": "key", "valueStr": "enemy_atk_down"},
                        {"key": "atk", "value": floor_difficulty_rate},
                    ],
                },
                {
                    "key": "global_buff_normal",
                    "blackboard": [
                        {"key": "key", "valueStr": "enemy_max_hp_down"},
                        {"key": "max_hp", "value": floor_difficulty_rate},
                        {
                            "key": "selector.enemy_exclude",
                            "valueStr": "enemy_1196_msfyin_2|enemy_1200_msfjin_2|enemy_1202_msfzhi_2|enemy_1208_msfji_2|enemy_1210_msfden_2|enemy_1198_msfshu_2",
                        },
                        {"key": "selector.profession", "valueStr": "none"},
                    ],
                },
            ]
        return stage_buff_lst


class Rlv2Theme5BasicManager(Rlv2BasicManager):
    def rlv2_createGame(self):
        super().rlv2_createGame()
        self.player_data["rlv2"]["current"]["player"]["property"]["gold"] = 500

    def get_raidian_buff_lst(self, stage_floor):
        raidian_buff_lst = []

        if stage_floor > 1:
            stage_floor -= 1

            raidian_buff_lst += [
                {
                    "key": "char_attribute_add",
                    "blackboard": [
                        {"key": "max_deploy_count", "value": 2},
                        {
                            "key": "selector.char",
                            "valueStr": "token_10051_radian_tower1|token_10052_radian_tower2|token_10053_radian_tower3",
                        },
                    ],
                },
            ]

        if stage_floor > 1:
            stage_floor -= 1

            raidian_buff_lst += [
                {
                    "key": "char_attribute_add",
                    "blackboard": [
                        {"key": "attack_speed", "value": 35},
                        {
                            "key": "selector.char",
                            "valueStr": "token_10051_radian_tower1|token_10052_radian_tower2|token_10053_radian_tower3",
                        },
                    ],
                },
            ]

        if stage_floor > 1:
            stage_floor -= 1

            raidian_buff_lst += [
                {
                    "key": "deck_card_buff",
                    "blackboard": [
                        {"key": "dont_occupy_deploy_cnt", "value": 1},
                        {
                            "key": "selector.char",
                            "valueStr": "token_10051_radian_tower1|token_10052_radian_tower2|token_10053_radian_tower3",
                        },
                    ],
                },
                {
                    "key": "char_ability_new_at_root",
                    "blackboard": [
                        {"key": "key", "valueStr": "rogue_2_occupy_zero[token]"},
                        {
                            "key": "selector.char",
                            "valueStr": "token_10051_radian_tower1|token_10052_radian_tower2|token_10053_radian_tower3",
                        },
                    ],
                },
            ]

        return raidian_buff_lst

    def get_unkeep_buff(self):
        unkeep_buff = super().get_unkeep_buff()

        stage_id = self.request_json["stageId"]
        stage_floor = self.get_stage_floor(stage_id)

        raidian_buff_lst = self.get_raidian_buff_lst(stage_floor)

        unkeep_buff += raidian_buff_lst

        return unkeep_buff

    def get_stage_buff_lst(self, floor_difficulty):
        stage_id = self.request_json["stageId"]

        stage_floor = self.get_stage_floor(stage_id)

        stage_buff_lst = []

        floor_difficulty_rate = 1 + 0.01 * floor_difficulty

        stage_buff_lst += [
            {
                "key": "zone_into_buff",
                "blackboard": [
                    {"key": "buff", "valueStr": "global_buff_normal"},
                    {"key": "key", "valueStr": "enemy_atk_down"},
                    {"key": "atk", "value": floor_difficulty_rate},
                    {
                        "key": "selector.enemy_exclude",
                        "valueStr": "enemy_10061_cjglon|enemy_10062_cjblon",
                    },
                ],
            },
            {
                "key": "zone_into_buff",
                "blackboard": [
                    {"key": "buff", "valueStr": "global_buff_normal"},
                    {"key": "key", "valueStr": "enemy_max_hp_down"},
                    {"key": "max_hp", "value": floor_difficulty_rate},
                    {
                        "key": "selector.enemy_exclude",
                        "valueStr": "enemy_1196_msfyin|enemy_1196_msfyin_2|enemy_1198_msfshu|enemy_1198_msfshu_2|enemy_1200_msfjin|enemy_1200_msfjin_2|enemy_1202_msfzhi|enemy_1202_msfzhi_2|enemy_1204_msfhu|enemy_1204_msfhu_2|enemy_1206_msfpin|enemy_1206_msfpin_2|enemy_1208_msfji|enemy_1208_msfji_2|enemy_1210_msfden|enemy_1210_msfden_2|enemy_10059_cjgfod|enemy_10060_cjbfod|enemy_2121_dyspl2|enemy_2101_dyspll",
                    },
                ],
            },
        ]

        for i in range(stage_floor):
            stage_buff_lst += [
                {
                    "key": "global_buff_normal",
                    "blackboard": [
                        {"key": "key", "valueStr": "enemy_atk_down"},
                        {"key": "atk", "value": floor_difficulty_rate},
                        {
                            "key": "selector.enemy_exclude",
                            "valueStr": "enemy_10061_cjglon|enemy_10062_cjblon",
                        },
                    ],
                },
                {
                    "key": "global_buff_normal",
                    "blackboard": [
                        {"key": "key", "valueStr": "enemy_max_hp_down"},
                        {"key": "max_hp", "value": floor_difficulty_rate},
                        {
                            "key": "selector.enemy_exclude",
                            "valueStr": "enemy_1196_msfyin|enemy_1196_msfyin_2|enemy_1198_msfshu|enemy_1198_msfshu_2|enemy_1200_msfjin|enemy_1200_msfjin_2|enemy_1202_msfzhi|enemy_1202_msfzhi_2|enemy_1204_msfhu|enemy_1204_msfhu_2|enemy_1206_msfpin|enemy_1206_msfpin_2|enemy_1208_msfji|enemy_1208_msfji_2|enemy_1210_msfden|enemy_1210_msfden_2|enemy_10059_cjgfod|enemy_10060_cjbfod|enemy_2121_dyspl2|enemy_2101_dyspll",
                        },
                    ],
                },
            ]
        return stage_buff_lst


def get_rlv2_manager(player_data, request_json, response):
    theme_id = player_data["rlv2"]["current"]["game"]["theme"]
    if theme_id == "rogue_1":
        return Rlv2Theme1BasicManager(player_data, theme_id, request_json, response)
    if theme_id == "rogue_2":
        return Rlv2Theme2BasicManager(player_data, theme_id, request_json, response)
    if theme_id == "rogue_4":
        return Rlv2Theme4BasicManager(player_data, theme_id, request_json, response)
    if theme_id == "rogue_5":
        return Rlv2Theme5BasicManager(player_data, theme_id, request_json, response)
    return Rlv2BasicManager(player_data, theme_id, request_json, response)


@bp_rlv2.route("/rlv2/createGame", methods=["POST"])
@player_data_decorator
def rlv2_createGame(player_data):
    request_json = request.get_json()
    response = {}

    mode = request_json["mode"]
    if mode == "MONTH_TEAM" or mode == "CHALLENGE":
        return "", 404

    theme_id = request_json["theme"]
    player_data["rlv2"]["current"]["game"] = {"theme": theme_id}

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_createGame()

    return response


@bp_rlv2.route("/rlv2/giveUpGame", methods=["POST"])
@player_data_decorator
def rlv2_giveUpGame(player_data):
    request_json = request.get_json()
    response = {"result": "ok"}

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_giveUpGame()

    return response


@bp_rlv2.route("/rlv2/chooseInitialRelic", methods=["POST"])
@player_data_decorator
def rlv2_chooseInitialRelic(player_data):
    request_json = request.get_json()
    response = {}

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_chooseInitialRelic()

    return response


@bp_rlv2.route("/rlv2/chooseInitialRecruitSet", methods=["POST"])
@player_data_decorator
def rlv2_chooseInitialRecruitSet(player_data):
    request_json = request.get_json()
    response = {}

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_chooseInitialRecruitSet()

    return response


@bp_rlv2.route("/rlv2/finishEvent", methods=["POST"])
@player_data_decorator
def rlv2_finishEvent(player_data):
    request_json = request.get_json()
    response = {}

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_finishEvent()

    return response


@bp_rlv2.route("/rlv2/moveTo", methods=["POST"])
@player_data_decorator
def rlv2_moveTo(player_data):
    request_json = request.get_json()
    response = {}

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_moveTo()

    return response


@bp_rlv2.route("/rlv2/shopAction", methods=["POST"])
@player_data_decorator
def rlv2_shopAction(player_data):
    request_json = request.get_json()
    response = {}

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_shopAction()

    return response


@bp_rlv2.route("/rlv2/moveAndBattleStart", methods=["POST"])
@player_data_decorator
def rlv2_moveAndBattleStart(player_data):
    request_json = request.get_json()
    response = {}

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_moveAndBattleStart()

    return response


@bp_rlv2.route("/rlv2/battleFinish", methods=["POST"])
@player_data_decorator
def rlv2_battleFinish(player_data):
    request_json = request.get_json()
    response = {}

    log_battle_log_if_necessary(player_data, request_json["data"])

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_battleFinish()

    return response


@bp_rlv2.route("/rlv2/finishBattleReward", methods=["POST"])
@player_data_decorator
def rlv2_finishBattleReward(player_data):
    request_json = request.get_json()
    response = {}

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_finishBattleReward()

    return response


@bp_rlv2.route("/rlv2/recruitChar", methods=["POST"])
@player_data_decorator
def rlv2_recruitChar(player_data):
    request_json = request.get_json()
    response = {}

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_recruitChar()

    return response


@bp_rlv2.route("/rlv2/closeRecruitTicket", methods=["POST"])
@player_data_decorator
def rlv2_closeRecruitTicket(player_data):
    request_json = request.get_json()
    response = {}

    rlv2_manager = get_rlv2_manager(player_data, request_json, response)

    rlv2_manager.rlv2_closeRecruitTicket()

    return response


@bp_rlv2.route("/rlv2/setPinned", methods=["POST"])
@player_data_decorator
def rlv2_setPinned(player_data):
    request_json = request.get_json()

    theme_id = request_json["id"]

    player_data["rlv2"]["pinned"] = theme_id

    response = {}
    return response
