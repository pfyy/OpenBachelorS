import psycopg
from psycopg.types.json import Json
from psycopg_pool import ConnectionPool

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON
from .const_json_loader import const_json_loader


DATABASE_NAME = "openbachelor"


def get_db_url():
    return const_json_loader[CONFIG_JSON]["db_url"]


db_conn_pool = ConnectionPool(get_db_url())


def get_db_conn():
    return db_conn_pool.connection()


def init_db():
    db_url = get_db_url()
    with psycopg.connect(db_url, autocommit=True) as conn:
        try:
            conn.execute(f"CREATE DATABASE {DATABASE_NAME} ENCODING UTF8")
        except Exception:
            pass

    with get_db_conn() as conn:
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


if const_json_loader[CONFIG_JSON]["use_db"]:
    try:
        init_db()
        IS_DB_READY = True
    except Exception:
        print("warn: init db failed, fallback to file save")
        IS_DB_READY = False
else:
    IS_DB_READY = False
