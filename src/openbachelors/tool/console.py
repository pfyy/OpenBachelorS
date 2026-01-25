import traceback
from functools import wraps
import asyncio

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, SANDBOX_PERM_TABLE
from ..util.const_json_loader import const_json_loader, ConstJson
from ..util.player_data import PlayerData, player_data_template
from ..util.helper import get_char_num_id
from ..util.db_manager import IS_DB_READY, destroy_db, init_db


def become_sync(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        asyncio.run(f(*args, **kwargs))

    wrapper.async_func = f

    return wrapper


@click.group(invoke_without_command=True)
@click.option("--interactive", "-i", is_flag=True)
@click.pass_context
def cli(ctx, interactive):
    ctx.ensure_object(dict)

    if interactive:
        session = PromptSession(
            history=FileHistory("console.txt"),
        )

        while True:
            try:
                text = session.prompt("> ")
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

            try:
                argv = text.split()
                cli(argv, standalone_mode=False)
            except Exception:
                traceback.print_exc()

        exit()


def configure_current_equip(player_data, char_num_id, evolve_phase):
    char_obj = player_data["troop"]["chars"][str(char_num_id)]
    if "tmpl" in char_obj:
        for tmpl_id, tmpl_obj in char_obj["tmpl"]:
            if evolve_phase < 2:
                current_equip = None
            else:
                current_equip = player_data_template["troop"]["chars"][
                    str(char_num_id)
                ]["tmpl"][tmpl_id]["currentEquip"]

            tmpl_obj["currentEquip"] = current_equip
    else:
        if evolve_phase < 2:
            current_equip = None
        else:
            current_equip = player_data_template["troop"]["chars"][str(char_num_id)][
                "currentEquip"
            ]
        char_obj["currentEquip"] = current_equip


@cli.command()
@click.option("-p", "--player-id", required=True)
@click.option("-c", "--char-id", required=True)
@click.option("--potential-rank", type=int)
@click.option("--favor-point", type=int)
@click.option("--evolve-phase", type=int)
@click.option("--level", type=int)
@click.option("--main-skill-lvl", type=int)
@click.option("--skill-idx", "skill_idx_lst", multiple=True, type=int)
@click.option("--specialize-level", type=int)
@click.option("--equip-id", "equip_id_lst", multiple=True)
@click.option("--equip-level", type=int)
@click.option("--tmpl-id")
@click.pass_context
@become_sync
async def char(
    ctx,
    player_id,
    char_id,
    potential_rank,
    favor_point,
    evolve_phase,
    level,
    main_skill_lvl,
    skill_idx_lst,
    specialize_level,
    equip_id_lst,
    equip_level,
    tmpl_id,
):
    player_data = await PlayerData.create(player_id)

    char_num_id = get_char_num_id(char_id)

    if potential_rank is not None:
        player_data["troop"]["chars"][str(char_num_id)]["potentialRank"] = (
            potential_rank
        )

    if favor_point is not None:
        player_data["troop"]["chars"][str(char_num_id)]["favorPoint"] = favor_point

    if evolve_phase is not None:
        player_data["troop"]["chars"][str(char_num_id)]["evolvePhase"] = evolve_phase
        configure_current_equip(player_data, char_num_id, evolve_phase)

    if level is not None:
        player_data["troop"]["chars"][str(char_num_id)]["level"] = level

    if main_skill_lvl is not None:
        player_data["troop"]["chars"][str(char_num_id)]["mainSkillLvl"] = main_skill_lvl

    if skill_idx_lst:
        if specialize_level is not None:
            if tmpl_id is None:
                for skill_idx in skill_idx_lst:
                    skill_lst = player_data["troop"]["chars"][str(char_num_id)][
                        "skills"
                    ].copy()
                    skill_lst[skill_idx]["specializeLevel"] = specialize_level
                    player_data["troop"]["chars"][str(char_num_id)]["skills"] = (
                        skill_lst
                    )
            else:
                for skill_idx in skill_idx_lst:
                    skill_lst = player_data["troop"]["chars"][str(char_num_id)]["tmpl"][
                        tmpl_id
                    ]["skills"].copy()
                    skill_lst[skill_idx]["specializeLevel"] = specialize_level
                    player_data["troop"]["chars"][str(char_num_id)]["tmpl"][tmpl_id][
                        "skills"
                    ] = skill_lst

    if equip_id_lst:
        if equip_level is not None:
            if tmpl_id is None:
                for equip_id in equip_id_lst:
                    player_data["troop"]["chars"][str(char_num_id)]["equip"][equip_id][
                        "level"
                    ] = equip_level
            else:
                for equip_id in equip_id_lst:
                    player_data["troop"]["chars"][str(char_num_id)]["tmpl"][tmpl_id][
                        "equip"
                    ][equip_id]["level"] = equip_level

    await player_data.save()


@cli.group()
@click.option("-p", "--player-id", required=True)
@click.option("-t", "--topic-id", required=True)
@click.pass_context
def sandbox(
    ctx,
    player_id,
    topic_id,
):
    ctx.obj["player_id"] = player_id
    ctx.obj["topic_id"] = topic_id


def get_next_enemy_rush_id(player_data, topic_id):
    enemy_rush_idx = 1
    while True:
        enemy_rush_id = f"er_{enemy_rush_idx}"
        if (
            enemy_rush_id
            not in player_data["sandboxPerm"]["template"]["SANDBOX_V2"][topic_id][
                "main"
            ]["enemy"]["enemyRush"]
        ):
            break
        enemy_rush_idx += 1

    return enemy_rush_id


enemy_rush_type_dict = ConstJson(
    {
        "NORMAL": 0,
        "ELITE": 1,
        "BOSS": 2,
        "BANDIT": 3,
        "RALLY": 4,
        "THIEF": 5,
    }
)


@sandbox.command()
@click.option("--enemy-id", required=True)
@click.option("--node-id", required=True)
@click.pass_context
@become_sync
async def enemy_rush(
    ctx,
    enemy_id,
    node_id,
):
    player_id = ctx.obj["player_id"]
    topic_id = ctx.obj["topic_id"]

    player_data = await PlayerData.create(player_id)

    enemy_rush_id = get_next_enemy_rush_id(player_data, topic_id)

    sandbox_perm_table = const_json_loader[SANDBOX_PERM_TABLE]

    enemy_rush_type = 0
    enemy_lst = []

    found = False
    for enemy_rush_type_str, enemy_rush_type_lst in sandbox_perm_table["detail"][
        "SANDBOX_V2"
    ][topic_id]["rushEnemyData"]["rushEnemyGroupConfigs"]:
        for i, enemy_rush_type_obj in enemy_rush_type_lst:
            if enemy_rush_type_obj["enemyGroupKey"] == enemy_id:
                found = True
                enemy_rush_type = enemy_rush_type_dict[enemy_rush_type_str]
                for j, enemy_obj in enemy_rush_type_obj["enemy"]:
                    enemy_cnt = enemy_obj["count"]
                    enemy_lst.append([enemy_cnt, enemy_cnt])
                break
        if found:
            break
    if not found:
        click.echo("err: enemy id not found")
        return

    enemy_rush_obj = {
        "enemyRushType": enemy_rush_type,
        "groupKey": enemy_id,
        "state": 0,
        "day": 0,
        "path": [
            node_id,
        ],
        "enemy": enemy_lst,
        "badge": 0,
        "src": {"type": 0, "id": ""},
    }

    player_data["sandboxPerm"]["template"]["SANDBOX_V2"][topic_id]["main"]["enemy"][
        "enemyRush"
    ][enemy_rush_id] = enemy_rush_obj

    await player_data.save()


@sandbox.command()
@click.option("--season-idx", required=True, type=int)
@click.pass_context
@become_sync
async def season(
    ctx,
    season_idx,
):
    player_id = ctx.obj["player_id"]
    topic_id = ctx.obj["topic_id"]

    player_data = await PlayerData.create(player_id)

    player_data["sandboxPerm"]["template"]["SANDBOX_V2"][topic_id]["main"]["map"][
        "season"
    ]["type"] = season_idx

    await player_data.save()


@cli.group()
@click.option("-p", "--player-id", required=True)
@click.pass_context
def rlv2(
    ctx,
    player_id,
):
    ctx.obj["player_id"] = player_id


@rlv2.command()
@click.option("--relic-id", required=True)
@click.option("--layer", required=True, type=int)
@click.pass_context
@become_sync
async def relic_layer(
    ctx,
    relic_id,
    layer,
):
    player_id = ctx.obj["player_id"]

    player_data = await PlayerData.create(player_id)

    for relic_inst_id, relic_obj in player_data["rlv2"]["current"]["inventory"][
        "relic"
    ]:
        if relic_obj["id"] == relic_id:
            relic_obj["layer"] = layer

    await player_data.save()


@rlv2.command()
@click.option("-n", required=True, type=int)
@click.pass_context
@become_sync
async def difficulty(
    ctx,
    n,
):
    player_id = ctx.obj["player_id"]

    player_data = await PlayerData.create(player_id)

    player_data["rlv2"]["current"]["game"]["modeGrade"] = n
    player_data["rlv2"]["current"]["game"]["equivalentGrade"] = n

    await player_data.save()


@rlv2.command()
@click.option("-c", "--char-id", required=True)
@click.option("--char-buff-id", required=True)
@click.pass_context
@become_sync
async def char_buff(
    ctx,
    char_id,
    char_buff_id,
):
    player_id = ctx.obj["player_id"]

    player_data = await PlayerData.create(player_id)

    for char_inst_id, char_obj in player_data["rlv2"]["current"]["troop"]["chars"]:
        if char_obj["charId"] == char_id:
            char_obj["charBuff"] = [char_buff_id]

    await player_data.save()


@cli.command()
@click.option("-p", "--player-id", required=True)
@click.option("-k", "--key", required=True)
@click.pass_context
@become_sync
async def reset_key(
    ctx,
    player_id,
    key,
):
    player_data = await PlayerData.create(player_id)

    player_data.reset_key(key)

    await player_data.save()

    click.echo("info: relogin is required for changes to take effect")


@cli.command()
@click.option("-p", "--player-id", required=True)
@click.pass_context
@become_sync
async def reset_all(
    ctx,
    player_id,
):
    player_data = await PlayerData.create(player_id)

    player_data.reset()

    await player_data.save()

    click.echo("info: relogin is required for changes to take effect")


@cli.command()
@click.pass_context
def reset_db(
    ctx,
):
    if IS_DB_READY:
        destroy_db()
        init_db()


if __name__ == "__main__":
    cli()
