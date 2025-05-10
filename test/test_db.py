from ..src.util.db_manager import IS_DB_READY, get_db_conn


def test_table():
    if IS_DB_READY:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM player_data")
