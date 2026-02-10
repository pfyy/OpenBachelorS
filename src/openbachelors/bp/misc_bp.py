import random

from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, ACTIVITY_TABLE
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.battle_log_logger import log_battle_log_if_necessary

router = APIRouter()


@router.post("/deepSea/branch")
@player_data_decorator
async def deepSea_branch(player_data, request: Request):
    request_json = await request.json()

    for branch in request_json["branches"]:
        tech_tree_id = branch["techTreeId"]
        branch_id = branch["branchId"]

        player_data["deepSea"]["techTrees"][tech_tree_id]["branch"] = branch_id

    response = {}
    return response


@router.post("/act25side/battleStart")
@player_data_decorator
async def act25side_battleStart(player_data, request: Request):
    request_json = await request.json()

    stage_id = request_json["stageId"]
    player_data.extra_save.save_obj["cur_stage_id"] = stage_id

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
        "apFailReturn": 0,
        "isApProtect": 0,
        "inApProtectPeriod": false,
        "notifyPowerScoreNotEnoughIfFailed": false,
    }
    return response


@router.post("/act25side/battleFinish")
@player_data_decorator
async def act25side_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "apFailReturn": 0,
        "expScale": 1.2,
        "goldScale": 1.2,
        "rewards": [],
        "firstRewards": [],
        "unlockStages": [],
        "unusualRewards": [],
        "additionalRewards": [],
        "furnitureRewards": [],
        "overrideRewards": [],
        "alert": [],
        "suggestFriend": false,
        "pryResult": [],
        "itemReturn": [],
    }
    return response


@router.post("/charm/setSquad")
@player_data_decorator
async def charm_setSquad(player_data, request: Request):
    request_json = await request.json()

    player_data["charm"]["squad"] = request_json["squad"]

    response = {}
    return response


@router.post("/car/confirmBattleCar")
@player_data_decorator
async def car_confirmBattleCar(player_data, request: Request):
    request_json = await request.json()

    player_data["car"]["battleCar"] = request_json["car"]

    response = {}
    return response


@router.post("/retro/typeAct20side/competitionStart")
@player_data_decorator
async def retro_typeAct20side_competitionStart(player_data, request: Request):
    request_json = await request.json()
    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/retro/typeAct20side/competitionFinish")
@player_data_decorator
async def retro_typeAct20side_competitionFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "performance": 0,
        "expression": 0,
        "operation": 0,
        "total": 0,
        "level": "SS",
        "isNew": false,
    }
    return response


@router.post("/trainingGround/battleStart")
@player_data_decorator
async def trainingGround_battleStart(player_data, request: Request):
    request_json = await request.json()
    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/trainingGround/battleFinish")
@player_data_decorator
async def trainingGround_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "firstRewards": [],
    }
    return response


@router.post("/medal/setCustomData")
@player_data_decorator
async def medal_setCustomData(player_data, request: Request):
    request_json = await request.json()

    custom_data = request_json["data"]

    player_data["medal"]["custom"]["customs"]["1"] = custom_data

    response = {}
    return response


@router.post("/firework/savePlateSlots")
@player_data_decorator
async def firework_savePlateSlots(player_data, request: Request):
    request_json = await request.json()

    player_data["firework"]["plate"]["slots"] = request_json["slots"]

    response = {}
    return response


@router.post("/firework/changeAnimal")
@player_data_decorator
async def firework_changeAnimal(player_data, request: Request):
    request_json = await request.json()

    player_data["firework"]["animal"]["select"] = request_json["animal"]

    response = {
        "animal": request_json["animal"],
    }
    return response


@router.post("/activity/enemyDuel/singleBattleStart")
@player_data_decorator
async def activity_enemyDuel_singleBattleStart(player_data, request: Request):
    request_json = await request.json()

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/activity/enemyDuel/singleBattleFinish")
@player_data_decorator
async def activity_enemyDuel_singleBattleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    activity_id = request_json["activityId"]
    activity_table = const_json_loader[ACTIVITY_TABLE]

    rank_lst = [
        {"id": "1", "rank": 1, "score": 262900, "isPlayer": 1},
    ]

    for npc_id, npc_obj in activity_table["activity"]["ENEMY_DUEL"][activity_id][
        "npcData"
    ]:
        if len(rank_lst) >= 8:
            break
        rank_lst.append(
            {"id": npc_id, "rank": 2, "score": 0, "isPlayer": 0},
        )

    response = {
        "result": 0,
        "choiceCnt": {"skip": 0, "normal": 5, "allIn": 5},
        "commentId": "Comment_Operation_1",
        "isHighScore": false,
        "rankList": rank_lst,
        "bp": 0,
        "dailyMission": {"add": 0, "reward": 0},
    }
    return response


@router.post("/activity/vecBreakV2/battleStart")
@player_data_decorator
async def activity_vecBreakV2_battleStart(player_data, request: Request):
    request_json = await request.json()

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/activity/vecBreakV2/battleFinish")
@player_data_decorator
async def activity_vecBreakV2_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "msBefore": 0,
        "msAfter": 0,
        "unlockStages": [],
        "suggestFriend": false,
        "finTs": 1700000000,
    }
    return response


@router.post("/vecBreakV2/getSeasonRecord")
@player_data_decorator
async def vecBreakV2_getSeasonRecord(player_data, request: Request):
    request_json = await request.json()

    response = {
        "seasons": {},
    }
    return response


def get_vec_break_v2_defense_buff_id(activity_id, stage_id):
    activity_table = const_json_loader[ACTIVITY_TABLE]

    defense_buff_id = activity_table["activity"]["VEC_BREAK_V2"][activity_id][
        "defenseDetailDict"
    ][stage_id]["buffId"]

    return defense_buff_id


@router.post("/activity/vecBreakV2/defendBattleStart")
@player_data_decorator
async def activity_vecBreakV2_defendBattleStart(player_data, request: Request):
    request_json = await request.json()

    activity_id = request_json["activityId"]
    stage_id = request_json["stageId"]

    defense_buff_id = get_vec_break_v2_defense_buff_id(activity_id, stage_id)

    defense_buff_id_lst = player_data["activity"]["VEC_BREAK_V2"][activity_id][
        "activatedBuff"
    ].copy()
    if defense_buff_id not in defense_buff_id_lst:
        defense_buff_id_lst.append(defense_buff_id)
    player_data["activity"]["VEC_BREAK_V2"][activity_id]["activatedBuff"] = (
        defense_buff_id_lst
    )

    player_data["activity"]["VEC_BREAK_V2"][activity_id]["defendStages"][stage_id][
        "defendSquad"
    ] = [{"charInstId": i["charInstId"]} for i in request_json["squad"]["slots"]]

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/activity/vecBreakV2/defendBattleFinish")
@player_data_decorator
async def activity_vecBreakV2_defendBattleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "msBefore": 0,
        "msAfter": 0,
        "finTs": 1700000000,
    }
    return response


@router.post("/activity/vecBreakV2/setDefend")
@player_data_decorator
async def activity_vecBreakV2_setDefend(player_data, request: Request):
    request_json = await request.json()

    activity_id = request_json["activityId"]
    stage_id = request_json["stageId"]

    defense_buff_id = get_vec_break_v2_defense_buff_id(activity_id, stage_id)

    defense_buff_id_lst = player_data["activity"]["VEC_BREAK_V2"][activity_id][
        "activatedBuff"
    ].copy()
    if defense_buff_id in defense_buff_id_lst:
        defense_buff_id_lst.remove(defense_buff_id)
    player_data["activity"]["VEC_BREAK_V2"][activity_id]["activatedBuff"] = (
        defense_buff_id_lst
    )

    player_data["activity"]["VEC_BREAK_V2"][activity_id]["defendStages"][stage_id][
        "defendSquad"
    ] = []

    response = {}
    return response


@router.post("/activity/vecBreakV2/changeBuffList")
@player_data_decorator
async def activity_vecBreakV2_changeBuffList(player_data, request: Request):
    request_json = await request.json()

    activity_id = request_json["activityId"]

    player_data["activity"]["VEC_BREAK_V2"][activity_id]["activatedBuff"] = (
        request_json["buffList"]
    )

    response = {}
    return response


@router.post("/activity/bossRush/battleStart")
@player_data_decorator
async def activity_bossRush_battleStart(player_data, request: Request):
    request_json = await request.json()

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
        "apFailReturn": 0,
        "isApProtect": 0,
        "inApProtectPeriod": false,
        "notifyPowerScoreNotEnoughIfFailed": false,
    }
    return response


@router.post("/activity/bossRush/battleFinish")
@player_data_decorator
async def activity_bossRush_battleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "result": 0,
        "apFailReturn": 0,
        "expScale": 0,
        "goldScale": 0,
        "rewards": [],
        "firstRewards": [],
        "unlockStages": [],
        "unusualRewards": [],
        "additionalRewards": [],
        "furnitureRewards": [],
        "alert": [],
        "suggestFriend": false,
        "pryResult": [],
        "wave": 3,
        "milestoneBefore": 0,
        "milestoneAdd": 0,
        "isMileStoneMax": true,
        "tokenAdd": 0,
        "isTokenMax": true,
    }
    return response


@router.post("/activity/bossRush/relicSelect")
@player_data_decorator
async def activity_bossRush_relicSelect(player_data, request: Request):
    request_json = await request.json()

    player_data["activity"]["BOSS_RUSH"][request_json["activityId"]]["relic"][
        "select"
    ] = request_json["relicId"]

    response = {}
    return response


@router.post("/activity/enemyDuel/startMatch")
@player_data_decorator
async def activity_enemyDuel_startMatch(player_data, request: Request):
    request_json = await request.json()

    player_data.extra_save.save_obj["enemyDuel_activityId"] = request_json["activityId"]
    player_data.extra_save.save_obj["enemyDuel_modeId"] = request_json["modeId"]

    response = {
        "result": 0,
    }
    return response


def get_server_token(player_data):
    activity_id = player_data.extra_save.save_obj["enemyDuel_activityId"]
    mode_id = player_data.extra_save.save_obj["enemyDuel_modeId"]

    stage_id = player_data["activity"]["ENEMY_DUEL"][activity_id]["modeInfo"][mode_id][
        "curStage"
    ]

    server_token = "|".join([mode_id, stage_id])

    return server_token


@router.post("/activity/enemyDuel/queryMatch")
@player_data_decorator
async def activity_enemyDuel_queryMatch(player_data, request: Request):
    request_json = await request.json()

    # if request_json["needLeave"]:
    #     response = {
    #         "result": 1,
    #         "team": null,
    #     }
    #     return response

    multiplayer_addr = const_json_loader[CONFIG_JSON]["multiplayer_addr"]

    server_token = get_server_token(player_data)

    response = {
        "result": 0,
        "team": {
            "teamId": "some_team_id",
            "serverAddress": multiplayer_addr,
            "serverToken": server_token,
        },
        "playerCnt": 8,
    }
    return response


@router.post("/activity/enemyDuel/multiBattleStart")
@player_data_decorator
async def activity_enemyDuel_multiBattleStart(player_data, request: Request):
    request_json = await request.json()

    response = {
        "result": 0,
    }
    return response


@router.post("/activity/enemyDuel/multiBattleFinish")
@player_data_decorator
async def activity_enemyDuel_multiBattleFinish(player_data, request: Request):
    request_json = await request.json()

    response = {
        "result": 0,
        "choiceCnt": {"skip": 0, "normal": 5, "allIn": 5},
        "commentId": "Comment_Operation_1",
        "isHighScore": false,
        "rankList": [
            {"id": "1", "rank": 1, "score": 262900, "isPlayer": 1},
            {
                "id": "100",
                "rank": 2,
                "score": 0,
                "isPlayer": 1,
                "playerBrief": {
                    "nickName": "Undergraduate",
                    "uid": "100",
                    "avatar": {"type": "ICON", "id": "avatar_def_01"},
                    "nickNumber": "1234",
                    "nameCardStyle": {
                        "componentOrder": [
                            "module_sign",
                            "module_assist",
                            "module_medal",
                        ],
                        "skin": {
                            "selected": "nc_rhodes_default",
                            "state": {},
                            "tmpl": {},
                        },
                        "misc": {"showDetail": true, "showBirthday": false},
                    },
                },
            },
        ],
        "bp": 0,
        "dailyMission": {"add": 0, "reward": 0},
    }
    return response


@router.post("/templateTrap/setTrapSquad")
@player_data_decorator
async def templateTrap_setTrapSquad(player_data, request: Request):
    request_json = await request.json()

    player_data["templateTrap"]["domains"][request_json["trapDomainId"]]["squad"] = (
        request_json["trapSquad"]
    )

    response = {}
    return response


@router.post("/activity/multiplayerV3/getInfo")
@player_data_decorator
async def activity_multiplayerV3_getInfo(player_data, request: Request):
    request_json = await request.json()

    response = {}
    return response


@router.post("/activity/multiplayerV3/changeTitle")
@player_data_decorator
async def activity_multiplayerV3_changeTitle(player_data, request: Request):
    request_json = await request.json()

    activity_id = request_json["activityId"]

    player_data["activity"]["MULTIPLAY_V3"][activity_id]["collection"]["title"][
        "select"
    ] = request_json["select"]

    response = {}
    return response


@router.post("/activity/multiplayerV3/setBuff")
@player_data_decorator
async def activity_multiplayerV3_setBuff(player_data, request: Request):
    request_json = await request.json()

    activity_id = request_json["activityId"]

    mode_id = request_json["modeType"]

    player_data["activity"]["MULTIPLAY_V3"][activity_id]["troop"]["squads"][mode_id][
        "buffId"
    ] = request_json["buffId"]

    response = {}
    return response


@router.post("/activity/multiplayerV3/setSquads")
@player_data_decorator
async def activity_multiplayerV3_setSquads(player_data, request: Request):
    request_json = await request.json()

    activity_id = request_json["activityId"]

    mode_id = request_json["modeType"]

    player_data["activity"]["MULTIPLAY_V3"][activity_id]["troop"]["squads"][mode_id][
        "prefer"
    ] = request_json["prefer"]
    player_data["activity"]["MULTIPLAY_V3"][activity_id]["troop"]["squads"][mode_id][
        "backup"
    ] = request_json["backup"]

    response = {}
    return response


@router.post("/activity/multiplayerV3/startMatch")
@player_data_decorator
async def activity_multiplayerV3_startMatch(player_data, request: Request):
    request_json = await request.json()

    activity_id = request_json["activityId"]

    player_data.extra_save.save_obj["icebreaker_activityId"] = activity_id
    player_data.extra_save.save_obj["icebreaker_modeList"] = request_json["option"][
        "modeList"
    ]

    player_data["activity"]["MULTIPLAY_V3"][activity_id]["match"]["lastModeList"] = (
        request_json["option"]["modeList"]
    )
    player_data["activity"]["MULTIPLAY_V3"][activity_id]["match"]["lastMentorType"] = (
        request_json["option"]["mentorType"]
    )
    player_data["activity"]["MULTIPLAY_V3"][activity_id]["match"]["lastReverse"] = (
        request_json["option"]["reverse"]
    )

    response = {
        "result": 0,
    }
    return response


def get_icebreaker_server_token(player_data):
    activity_id = player_data.extra_save.save_obj["icebreaker_activityId"]
    mode_id_lst = player_data.extra_save.save_obj["icebreaker_modeList"]

    server_token_arr = []

    activity_table = const_json_loader[ACTIVITY_TABLE]

    for mode_id in mode_id_lst:
        stage_id = random.choice(
            activity_table["activity"]["MULTIPLAY_V3"][activity_id]["mapTypeDataDict"][
                mode_id
            ]["stageIdInModeList"].copy()
        )
        server_token_arr.append(f"{mode_id},{stage_id}")

    server_token = "|".join(server_token_arr)

    return server_token


@router.post("/activity/multiplayerV3/queryMatch")
@player_data_decorator
async def activity_multiplayerV3_queryMatch(player_data, request: Request):
    request_json = await request.json()

    activity_id = request_json["activityId"]

    response = {}

    if request_json["needLeave"]:
        response["result"] = 1
        return response

    icebreaker_addr = const_json_loader[CONFIG_JSON]["icebreaker_addr"]

    server_token = get_icebreaker_server_token(player_data)

    response["result"] = 0
    response["team"] = {
        "mentorUid": "",
        "teamId": "some_team_id",
        "serverAddress": icebreaker_addr,
        "serverToken": server_token,
    }

    return response


@router.post("/activity/multiplayerV3/settleLike")
@player_data_decorator
async def activity_multiplayerV3_settleLike(player_data, request: Request):
    request_json = await request.json()

    response = {}
    return response


@router.post("/activity/multiplayerV3/battleStart")
@player_data_decorator
async def activity_multiplayerV3_battleStart(player_data, request: Request):
    request_json = await request.json()

    response = {
        "result": 0,
    }
    return response


@router.post("/activity/multiplayerV3/battleFinish")
@player_data_decorator
async def activity_multiplayerV3_battleFinish(player_data, request: Request):
    request_json = await request.json()

    response = {
        "data": {
            "result": 0,
            "mateQuit": false,
            "normal": {
                "failTip": false,
                "targets": [
                    {
                        "complete": true,
                        "progressShow": ["30", "30"],
                        "progressValue": [30, 30],
                    },
                    {
                        "complete": true,
                        "progressShow": ["5", "3"],
                        "progressValue": [5, 3],
                    },
                    {
                        "complete": true,
                        "progressShow": ["5", "5"],
                        "progressValue": [5, 5],
                    },
                ],
                "newStar": false,
            },
            "raft": {"score": 10000, "newScore": false},
            "defence": {
                "targets": [
                    {"complete": true, "progressValue": [4, 1]},
                    {"complete": true, "progressValue": [4, 2]},
                    {"complete": true, "progressValue": [4, 4]},
                ],
                "damage": 10000,
                "damagePct": 100,
                "bossKill": true,
                "newStar": false,
                "newDamage": false,
            },
            "star": 3,
            "reward": {
                "item": [],
                "milestoneAdd": 0,
                "gainDailyReward": false,
            },
            "newPhoto": false,
            "newPhotoId": "",
            "sameChannel": true,
            "isFriend": false,
            "reverse": 0,
            "ts": 1700000000,
        },
    }
    return response


@router.post("/activity/multiplayerV3/guideBattleStart")
@player_data_decorator
async def activity_multiplayerV3_guideBattleStart(player_data, request: Request):
    request_json = await request.json()

    response = {
        "result": 0,
        "battleId": "00000000-0000-0000-0000-000000000000",
    }
    return response


@router.post("/activity/multiplayerV3/guideBattleFinish")
@player_data_decorator
async def activity_multiplayerV3_guideBattleFinish(player_data, request: Request):
    request_json = await request.json()

    log_battle_log_if_necessary(player_data, request_json["data"])

    response = {
        "data": {
            "result": 0,
            "mateQuit": false,
            "normal": {
                "failTip": false,
                "targets": [
                    {
                        "complete": true,
                        "progressShow": ["30", "30"],
                        "progressValue": [30, 30],
                    },
                    {
                        "complete": true,
                        "progressShow": ["5", "3"],
                        "progressValue": [5, 3],
                    },
                    {
                        "complete": true,
                        "progressShow": ["5", "5"],
                        "progressValue": [5, 5],
                    },
                ],
                "newStar": false,
            },
            "raft": {"score": 10000, "newScore": false},
            "defence": {
                "targets": [
                    {"complete": true, "progressValue": [4, 1]},
                    {"complete": true, "progressValue": [4, 2]},
                    {"complete": true, "progressValue": [4, 4]},
                ],
                "damage": 10000,
                "damagePct": 100,
                "bossKill": true,
                "newStar": false,
                "newDamage": false,
            },
            "star": 3,
            "reward": {"item": [], "milestoneAdd": 0, "gainDailyReward": false},
            "sameChannel": false,
            "isFriend": false,
            "reverse": 0,
            "ts": 1700000000,
            "newPhoto": false,
        },
    }
    return response


@router.post("/invite/switchInviteAccept")
@player_data_decorator
async def invite_switchInviteAccept(player_data, request: Request):
    request_json = await request.json()

    invite_id = request_json["inviteId"]
    invite_type = request_json["inviteType"]

    player_data["invite"][invite_type][invite_id]["closeAccept"] = bool(
        request_json["operate"]
    )

    response = {
        "result": 0,
    }
    return response


@router.post("/invite/refreshInviteList")
@player_data_decorator
async def invite_refreshInviteList(player_data, request: Request):
    request_json = await request.json()

    response = {}
    return response


@router.post("/gallery/getThumbnailUrl")
@player_data_decorator
async def gallery_getThumbnailUrl(player_data, request: Request):
    request_json = await request.json()

    num_id = len(request_json["idList"])

    response = {"url": [None for _ in range(num_id)]}
    return response


@router.post("/gallery/changeMagazineSquad")
@player_data_decorator
async def gallery_changeMagazineSquad(player_data, request: Request):
    request_json = await request.json()

    player_data["gallery"]["magazineSquad"] = request_json["squad"]

    response = {}
    return response


@router.post("/gallery/saveDiyMagazineV1")
@player_data_decorator
async def gallery_saveDiyMagazineV1(player_data, request: Request):
    request_json = await request.json()

    magazine_obj = request_json["magazine"]

    leaf_id = magazine_obj["leafId"]

    player_data["gallery"]["leafMap"][leaf_id]["charSkin"] = magazine_obj["charSkin"]
    player_data["gallery"]["leafMap"][leaf_id]["decorList"] = magazine_obj["decorList"]

    response = {}
    return response
