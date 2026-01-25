import pytest

from openbachelors.util.db_manager import IS_DB_READY, get_db_conn_or_pool


@pytest.mark.asyncio(loop_scope="session")
async def test_table(db_pool_fixture):
    if IS_DB_READY:
        pool = get_db_conn_or_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM player_data")
