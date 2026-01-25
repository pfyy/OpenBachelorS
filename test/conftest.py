import asyncio
import sys
import pytest_asyncio

from openbachelors.util.db_manager import IS_DB_READY, get_db_conn_or_pool

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def db_pool_fixture():
    if IS_DB_READY:
        pool = get_db_conn_or_pool()
        await pool.open()

    yield

    if IS_DB_READY:
        await pool.close()
