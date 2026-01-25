import os
from abc import ABC, abstractmethod
from typing import List

from psycopg.types.json import Json

from .helper import (
    encode_stage_id,
    decode_stage_id,
    load_battle_replay_from_file,
    save_battle_replay_to_file,
    encode_battle_replay,
    decode_battle_replay,
)
from .db_manager import IS_DB_READY, get_db_conn_or_pool


class AbstractBattleReplayManager(ABC):
    @abstractmethod
    async def load_battle_replay(self, stage_id: str) -> str:
        pass

    @abstractmethod
    async def save_battle_replay(self, stage_id: str, battle_replay: str):
        pass

    @abstractmethod
    async def get_battle_replay_lst(self) -> List[str]:
        pass


class BattleReplayManager(AbstractBattleReplayManager):
    def __init__(self, dirpath: str):
        os.makedirs(dirpath, exist_ok=True)
        self.dirpath = dirpath

    def get_battle_replay_filepath(self, stage_id: str) -> str:
        return os.path.join(self.dirpath, f"{encode_stage_id(stage_id)}.json")

    async def load_battle_replay(self, stage_id: str) -> str:
        battle_replay_filepath = self.get_battle_replay_filepath(stage_id)
        return await load_battle_replay_from_file(battle_replay_filepath)

    async def save_battle_replay(self, stage_id: str, battle_replay: str):
        battle_replay_filepath = self.get_battle_replay_filepath(stage_id)
        await save_battle_replay_to_file(battle_replay_filepath, battle_replay)

    async def get_battle_replay_lst(self) -> List[str]:
        raw_battle_replay_lst = os.listdir(self.dirpath)

        battle_replay_lst = [
            decode_stage_id(os.path.splitext(i)[0]) for i in raw_battle_replay_lst
        ]

        return battle_replay_lst


class DBBattleReplayManager(AbstractBattleReplayManager):
    def __init__(self, username: str):
        self.username = username

    async def load_battle_replay(self, stage_id: str) -> str:
        pool = get_db_conn_or_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT battle_replay FROM battle_replay WHERE username = %s AND stage_id = %s",
                    (self.username, stage_id),
                )
                return encode_battle_replay((await cur.fetchone())[0])

    async def save_battle_replay(self, stage_id: str, battle_replay: str):
        decoded_battle_replay = Json(decode_battle_replay(battle_replay))
        pool = get_db_conn_or_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT 1 FROM battle_replay WHERE username = %s AND stage_id = %s",
                    (self.username, stage_id),
                )
                if await cur.fetchone():
                    await cur.execute(
                        "UPDATE battle_replay SET battle_replay = %s WHERE username = %s AND stage_id = %s",
                        (decoded_battle_replay, self.username, stage_id),
                    )
                else:
                    await cur.execute(
                        "INSERT INTO battle_replay VALUES (%s, %s, %s)",
                        (self.username, stage_id, decoded_battle_replay),
                    )
                await conn.commit()

    async def get_battle_replay_lst(self) -> List[str]:
        pool = get_db_conn_or_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT stage_id FROM battle_replay WHERE username = %s",
                    (self.username,),
                )
                return [t[0] for t in await cur.fetchall()]
