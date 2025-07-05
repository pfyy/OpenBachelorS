import psycopg
from psycopg.types.json import Json
from psycopg_pool import ConnectionPool

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON
from .const_json_loader import const_json_loader


DATABASE_NAME = "openbachelor"
DATABASE_TIMEOUT = 3


def get_db_url(with_database_name=True):
    db_url = const_json_loader[CONFIG_JSON]["db_url"]
    if with_database_name:
        return f"{db_url}/{DATABASE_NAME}?connect_timeout={DATABASE_TIMEOUT}"
    return f"{db_url}?connect_timeout={DATABASE_TIMEOUT}"


db_conn_pool = None


def get_db_conn(use_pool=True):
    global db_conn_pool
    db_url = get_db_url()
    if not use_pool:
        return psycopg.connect(db_url)
    if not db_conn_pool:
        db_conn_pool = ConnectionPool(db_url)
    return db_conn_pool.connection()


def init_db():
    with psycopg.connect(get_db_url(with_database_name=False), autocommit=True) as conn:
        try:
            conn.execute(f"CREATE DATABASE {DATABASE_NAME} ENCODING UTF8")
        except Exception:
            pass

    with get_db_conn(use_pool=False) as conn:
        conn.execute(
            """
CREATE TABLE IF NOT EXISTS player_data (
    username varchar(1024) PRIMARY KEY,
    delta json,
    pending_delta json,
    extra json
)
"""
        )

        conn.execute(
            """
CREATE TABLE IF NOT EXISTS battle_replay (
    username varchar(1024),
    stage_id varchar(1024),
    battle_replay json,
    PRIMARY KEY(username, stage_id)
)
"""
        )

        conn.commit()


def create_user_if_necessary(username):
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM player_data WHERE username = %s", (username,))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO player_data VALUES (%s, %s, %s, %s)",
                    (
                        username,
                        None,
                        None,
                        None,
                    ),
                )

                conn.commit()


def destroy_db():
    with psycopg.connect(get_db_url(with_database_name=False), autocommit=True) as conn:
        conn.execute(f"DROP DATABASE IF EXISTS {DATABASE_NAME}")


if const_json_loader[CONFIG_JSON]["use_db"]:
    try:
        init_db()
        IS_DB_READY = True
    except Exception:
        print("warn: init db failed, fallback to file save")
        IS_DB_READY = False
else:
    IS_DB_READY = False
