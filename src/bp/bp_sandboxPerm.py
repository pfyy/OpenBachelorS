from enum import Enum
import random
from functools import cmp_to_key

from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, SANDBOX_PERM_TABLE
from ..util.const_json_loader import const_json_loader, ConstJson
from ..util.player_data import player_data_decorator
from ..util.battle_log_logger import log_battle_log_if_necessary

bp_sandboxPerm = Blueprint("bp_sandboxPerm", __name__)


class SandboxBasicManager:
    def __init__(self, player_data, topic_id, request_json, response):
        self.player_data = player_data
        self.topic_id = topic_id
        self.request_json = request_json
        self.response = response

    def sandboxPerm_sandboxV2_setSquad(self):
        squad_lst = self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][
            self.topic_id
        ]["troop"]["squad"].copy()

        squad_idx = self.request_json["index"]

        squad_lst[squad_idx]["slots"] = self.request_json["slots"]
        squad_lst[squad_idx]["tools"] = self.request_json["tools"]

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "troop"
        ]["squad"] = squad_lst

    def calc_extra_rune(self):
        sandbox_perm_table = const_json_loader[SANDBOX_PERM_TABLE]

        if self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "status"
        ]["isChallenge"]:
            self.response["extraRunes"].append("challenge_daily")
            challenge_day = min(
                self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][
                    self.topic_id
                ]["main"]["game"]["day"],
                100,
            )
            for i in range(1, challenge_day):
                challenge_day_buff = f"challenge_day_{i}"
                if (
                    challenge_day_buff
                    in sandbox_perm_table["detail"]["SANDBOX_V2"][self.topic_id][
                        "runeDatas"
                    ]
                ):
                    self.response["extraRunes"].append(challenge_day_buff)

        squad_idx = self.request_json["squadIdx"]
        squad_tool_lst = self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][
            self.topic_id
        ]["troop"]["squad"][squad_idx]["tools"].copy()

        for squad_tool in squad_tool_lst:
            squad_tool_obj = sandbox_perm_table["detail"]["SANDBOX_V2"][self.topic_id][
                "itemTrapData"
            ][squad_tool]
            if "buffId" in squad_tool_obj:
                squad_tool_buff = squad_tool_obj["buffId"]

                if squad_tool_buff:
                    self.response["extraRunes"].append(squad_tool_buff)

    def sandboxPerm_sandboxV2_battleStart(self):
        self.response.update(
            {
                "battleId": "00000000-0000-0000-0000-000000000000",
                "isEnemyRush": false,
                "shinyAnimals": {},
                "shinyUniEnemy": [],
                "lureInsect": [],
                "extraRunes": [],
            }
        )

        self.calc_extra_rune()

        node_id = self.request_json["nodeId"]
        self.player_data.extra_save.save_obj["cur_node_id"] = node_id

    def sandboxPerm_sandboxV2_battleFinish(self):
        self.response.update(
            {
                "success": true,
                "rewards": [],
                "randomRewards": [],
                "costItems": [],
                "isEnemyRush": false,
                "enemyRushCount": [],
            }
        )

        if self.player_data.extra_save.save_obj.get("cur_node_id", None) is None:
            return

        node_id = self.player_data.extra_save.save_obj["cur_node_id"]

        node_building_lst = self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][
            self.topic_id
        ]["main"]["stage"]["node"][node_id]["building"].copy()

        for placed_item in self.request_json["sandboxV2Data"]["placedItems"]:
            if placed_item["value"]["hpRatio"]:
                building_op = self.BuildingOp.CONSTRUCT
            else:
                building_op = self.BuildingOp.DESTROY

            building_id = placed_item["key"]["itemId"]
            row = placed_item["key"]["position"]["row"]
            col = placed_item["key"]["position"]["col"]
            building_dir = placed_item["value"]["direction"]

            building_op_ret = self.execute_building_op(
                building_op, node_building_lst, row, col, building_dir, building_id
            )

            # presume that buff building can't be built this way
            if building_op is self.BuildingOp.DESTROY:
                building_id = building_op_ret
                if building_id is not None:
                    self.check_building_buff(building_id, building_op)

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "main"
        ]["stage"]["node"][node_id]["building"] = node_building_lst

    # code only for sandbox_1
    FOOD_SUB_RUNE_DICT = ConstJson({"sandbox_1_puree": "battle_sub_atk_15"})

    def sandboxPerm_sandboxV2_eatFood(self):
        char_num_id = self.request_json["charInstId"]

        food_inst_id = self.request_json["foodInstId"]
        food_obj = self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][
            self.topic_id
        ]["cook"]["food"][food_inst_id].copy()

        food_id = food_obj["id"]
        food_sub_lst = food_obj["sub"]

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "troop"
        ]["food"][str(char_num_id)] = {
            "id": food_id,
            "sub": food_sub_lst,
            "day": -1,
        }

        sandbox_perm_table = const_json_loader[SANDBOX_PERM_TABLE]

        food_rune_lst = []

        # code only for sandbox_1
        if food_sub_lst == ["sandbox_1_condiment", "sandbox_1_condiment"]:
            food_rune = f"{food_id}_x"
            if (
                food_rune
                not in sandbox_perm_table["detail"]["SANDBOX_V2"][self.topic_id][
                    "runeDatas"
                ]
            ):
                food_rune = food_id
        else:
            food_rune = food_id

        food_rune_lst.append(food_rune)

        for food_sub in food_sub_lst:
            if food_sub in self.FOOD_SUB_RUNE_DICT:
                food_sub_rune = self.FOOD_SUB_RUNE_DICT[food_sub]
                food_rune_lst.append(food_sub_rune)

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "buff"
        ]["rune"]["char"][str(char_num_id)] = food_rune_lst

    class BuildingOp(Enum):
        CONSTRUCT = 1
        DESTROY = 3

    @classmethod
    def execute_building_op(
        cls,
        building_op,
        node_building_lst,
        row,
        col,
        building_dir=None,
        building_id=None,
    ):
        building_pos = [row, col]

        building_idx = -1
        for i, building_obj in enumerate(node_building_lst):
            if building_obj["pos"] == building_pos:
                building_idx = i
                break

        if building_op is cls.BuildingOp.CONSTRUCT:
            building_obj = {
                "key": building_id,
                "pos": building_pos,
                "hpRatio": 10000,
                "dir": building_dir,
            }
            if building_idx == -1:
                node_building_lst.append(building_obj)
            else:
                # warn: can only overwrite building of the same kind (building buff issue)
                node_building_lst[building_idx] = building_obj
        elif building_op is cls.BuildingOp.DESTROY:
            if building_idx != -1:
                building_id = node_building_lst[building_idx]["key"]
                node_building_lst.pop(building_idx)
                return building_id

        return None

    class BuffOp(Enum):
        ADD = 0
        REMOVE = 1

    def execute_buff_op(self, buff_op, buff):
        buff_lst = self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][
            self.topic_id
        ]["buff"]["rune"]["global"].copy()

        if buff_op is self.BuffOp.ADD:
            buff_lst.append(buff)
        else:
            for i in range(len(buff_lst)):
                if buff_lst[i] == buff:
                    buff_lst.pop(i)
                    break

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "buff"
        ]["rune"]["global"] = buff_lst

    def check_building_buff(self, building_id, building_op):
        sandbox_perm_table = const_json_loader[SANDBOX_PERM_TABLE]

        building_obj = sandbox_perm_table["detail"]["SANDBOX_V2"][self.topic_id][
            "itemTrapData"
        ][building_id]

        if "buffId" in building_obj:
            building_buff = building_obj["buffId"]

            if building_buff:
                if building_op is self.BuildingOp.CONSTRUCT:
                    buff_op = self.BuffOp.ADD
                else:
                    buff_op = self.BuffOp.REMOVE
                self.execute_buff_op(buff_op, building_buff)

    def sandboxPerm_sandboxV2_homeBuildSave(self):
        node_id = self.request_json["nodeId"]

        node_building_lst = self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][
            self.topic_id
        ]["main"]["stage"]["node"][node_id]["building"].copy()

        operation_lst = self.request_json["operation"]
        for operation_obj in operation_lst:
            if operation_obj["type"] == 1:
                building_op = self.BuildingOp.CONSTRUCT
            elif operation_obj["type"] == 3:
                building_op = self.BuildingOp.DESTROY
            else:
                continue
            row = operation_obj["pos"]["row"]
            col = operation_obj["pos"]["col"]
            building_dir = operation_obj.get("dir", None)
            building_id = operation_obj.get("buildingId", None)
            building_op_ret = self.execute_building_op(
                building_op, node_building_lst, row, col, building_dir, building_id
            )
            if building_op is self.BuildingOp.DESTROY:
                building_id = building_op_ret
            if building_id is not None:
                self.check_building_buff(building_id, building_op)

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "main"
        ]["stage"]["node"][node_id]["building"] = node_building_lst

        animal_lst = []

        for room_id in self.request_json["catchedAnimals"]:
            room_obj = self.request_json["catchedAnimals"][room_id]

            enemy_lst = []

            for enemy_id in room_obj:
                enemy_lst.append({"id": enemy_id, "count": room_obj[enemy_id]})

            animal_lst.append({"room": int(room_id), "enemy": enemy_lst})

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "main"
        ]["stage"]["node"][node_id]["animal"] = animal_lst

    def sandboxPerm_sandboxV2_switchMode(self):
        mode = self.request_json["mode"]
        prev_mode = self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][
            self.topic_id
        ]["status"]["mode"]

        # code only for sandbox_1
        normal_mode_buff_lst = ["normal_mode_buff1", "normal_mode_buff3"]

        if mode == 0:
            for normal_mode_buff in normal_mode_buff_lst:
                self.execute_buff_op(self.BuffOp.REMOVE, normal_mode_buff)
        elif prev_mode == 0:
            for normal_mode_buff in normal_mode_buff_lst:
                self.execute_buff_op(self.BuffOp.ADD, normal_mode_buff)

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "status"
        ]["mode"] = mode

    def sandboxPerm_sandboxV2_monthBattleStart(self):
        self.response.update(
            {
                "battleId": "00000000-0000-0000-0000-000000000000",
                "extraRunes": [],
            }
        )

        self.calc_extra_rune()

    def sandboxPerm_sandboxV2_monthBattleFinish(self):
        self.response.update(
            {
                "success": true,
                "firstPass": false,
                "enemyRushCount": [0, 1],
            }
        )

    # code only for sandbox_1
    NODE_ID_NUM_RIVAL_DICT = ConstJson(
        {
            "nEB55": 4,
            "nACB1": 4,
            "n06C5": 4,
            "n36A1": 5,
            "n4BD8": 9,
            "n8594": 9,
            "n7EF6": 9,
            "nEF76": 9,
        }
    )

    def sandboxPerm_sandboxV2_racing_battleStart(self):
        node_id = self.request_json["nodeId"]

        racer_inst_id = self.request_json["instId"]
        self.player_data.extra_save.save_obj["cur_racer_inst_id"] = racer_inst_id

        sandbox_perm_table = const_json_loader[SANDBOX_PERM_TABLE]
        racer_id_lst = []
        for racer_id, racer_obj in sandbox_perm_table["detail"]["SANDBOX_V2"][
            self.topic_id
        ]["racingData"]["racerBasicInfo"]:
            racer_id_lst.append(racer_id)

        num_rival = self.NODE_ID_NUM_RIVAL_DICT[node_id]
        rival_lst = random.choices(racer_id_lst, k=num_rival)
        self.player_data.extra_save.save_obj["cur_rival_lst"] = rival_lst

        racer_lst = []
        for i, racer_id in enumerate(rival_lst):
            rival_inst_id = f"rr_{i}"
            racer_lst.append(
                {
                    "inst": rival_inst_id,
                    "id": racer_id,
                    "attrib": sandbox_perm_table["detail"]["SANDBOX_V2"][self.topic_id][
                        "racingData"
                    ]["racerBasicInfo"][racer_id]["attributeMaxValue"].copy(),
                    "skill": {"born": null, "learned": null},
                }
            )

        racer_obj = self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][
            self.topic_id
        ]["racing"]["bag"]["racer"][racer_inst_id].copy()
        racer_lst.append(
            {
                "inst": racer_inst_id,
                "id": racer_obj["id"],
                "attrib": racer_obj["attrib"],
                "skill": {"born": null, "learned": null},
            }
        )

        random.shuffle(racer_lst)

        self.response.update(
            {
                "battleId": "00000000-0000-0000-0000-000000000000",
                "myRacer": racer_inst_id,
                "racers": racer_lst,
            }
        )

    @staticmethod
    def rank_lst_cmp(lhs, rhs):
        if lhs["time"] != -1 and rhs["time"] != -1:
            return lhs["time"] - rhs["time"]
        if lhs["time"] != -1:
            return -1
        if rhs["time"] != -1:
            return 1
        return 0

    def sandboxPerm_sandboxV2_racing_battleFinish(self):
        racer_inst_id = self.player_data.extra_save.save_obj.get("cur_racer_inst_id")
        rival_lst = self.player_data.extra_save.save_obj["cur_rival_lst"]

        rank_lst = []
        for i, racer_id in enumerate(rival_lst):
            rival_inst_id = f"rr_{i}"
            rank_lst.append(
                {
                    "inst": rival_inst_id,
                    "name": {"prefix": "prefix_1", "suffix": "suffix_1"},
                    "id": racer_id,
                    "time": self.request_json["racingData"]["record"][rival_inst_id][
                        "time"
                    ],
                }
            )

        racer_obj = self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][
            self.topic_id
        ]["racing"]["bag"]["racer"][racer_inst_id].copy()
        rank_lst.append(
            {
                "inst": racer_inst_id,
                "name": racer_obj["name"],
                "id": racer_obj["id"],
                "time": self.request_json["racingData"]["record"][racer_inst_id][
                    "time"
                ],
            }
        )

        rank_lst.sort(key=cmp_to_key(self.rank_lst_cmp))

        self.response.update(
            {
                "giveUp": false,
                "myRacer": racer_inst_id,
                "ranklist": rank_lst,
                "bestTime": rank_lst[0]["time"],
                "myMedalId": null,
                "isNewBest": false,
                "rewards": [],
            }
        )

    CHALLENGE_DAY = 99999

    def update_hard_ratio(self):
        challenge_day = self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][
            self.topic_id
        ]["main"]["game"]["day"]
        hard_ratio = 10 + challenge_day * 1 + (challenge_day - 1) // 9 * 10
        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "challenge"
        ]["cur"]["hardRatio"] = hard_ratio

    def sandboxPerm_sandboxV2_enterChallenge(self):
        if (
            self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
                "status"
            ]["mode"]
            != 0
        ):
            pseudo_request_json = {"mode": 0}
            pseudo_sandbox_manager = self.__class__(
                self.player_data, self.topic_id, pseudo_request_json, {}
            )
            pseudo_sandbox_manager.sandboxPerm_sandboxV2_switchMode()
        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "challenge"
        ]["status"] = 1

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "challenge"
        ]["cur"] = {
            "instId": 1,
            "startDay": 1,
            "startLoadTimes": 0,
            "enemyKill": 0,
            "hardRatio": 11,
        }

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "status"
        ]["isChallenge"] = true

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "main"
        ]["game"]["day"] = self.CHALLENGE_DAY

        self.execute_buff_op(self.BuffOp.ADD, "season_rainy")

        self.update_hard_ratio()

    def sandboxPerm_sandboxV2_settleChallenge(self):
        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "challenge"
        ]["status"] = 2

    def sandboxPerm_sandboxV2_exitChallenge(self):
        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "challenge"
        ]["status"] = 0

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "challenge"
        ]["cur"] = null

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "status"
        ]["isChallenge"] = false

        self.player_data["sandboxPerm"]["template"]["SANDBOX_V2"][self.topic_id][
            "main"
        ]["game"]["day"] = 1

        self.execute_buff_op(self.BuffOp.REMOVE, "season_rainy")


def get_sandbox_manager(player_data, topic_id, request_json, response):
    return SandboxBasicManager(player_data, topic_id, request_json, response)


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/setSquad", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_setSquad(player_data):
    request_json = request.get_json()
    response = {}

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_setSquad()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/battleStart", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_battleStart(player_data):
    request_json = request.get_json()
    response = {}

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_battleStart()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/battleFinish", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_battleFinish(player_data):
    request_json = request.get_json()
    response = {}

    log_battle_log_if_necessary(player_data, request_json["data"])

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_battleFinish()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/eatFood", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_eatFood(player_data):
    request_json = request.get_json()
    response = {}

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_eatFood()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/homeBuildSave", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_homeBuildSave(player_data):
    request_json = request.get_json()
    response = {}

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_homeBuildSave()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/switchMode", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_switchMode(player_data):
    request_json = request.get_json()
    response = {}

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_switchMode()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/monthBattleStart", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_monthBattleStart(player_data):
    request_json = request.get_json()
    response = {}

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_monthBattleStart()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/monthBattleFinish", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_monthBattleFinish(player_data):
    request_json = request.get_json()
    response = {}

    log_battle_log_if_necessary(player_data, request_json["data"])

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_monthBattleFinish()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/racing/battleStart", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_racing_battleStart(player_data):
    request_json = request.get_json()
    response = {}

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_racing_battleStart()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/racing/battleFinish", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_racing_battleFinish(player_data):
    request_json = request.get_json()
    response = {}

    log_battle_log_if_necessary(player_data, request_json["data"])

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_racing_battleFinish()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/enterChallenge", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_enterChallenge(player_data):
    request_json = request.get_json()
    response = {}

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_enterChallenge()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/settleChallenge", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_settleChallenge(player_data):
    request_json = request.get_json()
    response = {}

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_settleChallenge()

    return response


@bp_sandboxPerm.route("/sandboxPerm/sandboxV2/exitChallenge", methods=["POST"])
@player_data_decorator
def sandboxPerm_sandboxV2_exitChallenge(player_data):
    request_json = request.get_json()
    response = {}

    topic_id = request_json["topicId"]

    sandbox_manager = get_sandbox_manager(player_data, topic_id, request_json, response)

    sandbox_manager.sandboxPerm_sandboxV2_exitChallenge()

    return response
