import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from .bp import (
    bp_account,
    bp_api,
    bp_app,
    bp_aprilFool,
    bp_assetbundle,
    bp_building,
    bp_businessCard,
    bp_campaignV2,
    bp_char,
    bp_charBuild,
    bp_charRotation,
    bp_common,
    bp_config,
    bp_crisisV2,
    bp_gacha,
    bp_general,
    bp_mail,
    bp_pay,
    bp_quest,
    bp_recalRune,
    bp_rlv2,
    bp_sandboxPerm,
    bp_settings,
    bp_shop,
    bp_social,
    bp_storyreview,
    bp_templateShop,
    bp_tower,
    bp_u8,
    bp_user,
    bp_yostar,
    legacy_bp,
    misc_bp,
)
from .util.db_manager import get_db_conn_or_pool, IS_DB_READY
from .util.helper import get_httpx_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    if IS_DB_READY:
        pool = get_db_conn_or_pool()
        await pool.open()

    httpx_client = get_httpx_client()

    yield

    if IS_DB_READY:
        await pool.close()

    await httpx_client.aclose()


app = FastAPI(lifespan=lifespan)


app.include_router(bp_account.router)
app.include_router(bp_api.router)
app.include_router(bp_app.router)
app.include_router(bp_aprilFool.router)
app.include_router(bp_assetbundle.router)
app.include_router(bp_building.router)
app.include_router(bp_businessCard.router)
app.include_router(bp_campaignV2.router)
app.include_router(bp_char.router)
app.include_router(bp_charBuild.router)
app.include_router(bp_charRotation.router)
app.include_router(bp_common.router)
app.include_router(bp_config.router)
app.include_router(bp_crisisV2.router)
app.include_router(bp_gacha.router)
app.include_router(bp_general.router)
app.include_router(bp_mail.router)
app.include_router(bp_pay.router)
app.include_router(bp_quest.router)
app.include_router(bp_recalRune.router)
app.include_router(bp_rlv2.router)
app.include_router(bp_sandboxPerm.router)
app.include_router(bp_settings.router)
app.include_router(bp_shop.router)
app.include_router(bp_social.router)
app.include_router(bp_storyreview.router)
app.include_router(bp_templateShop.router)
app.include_router(bp_tower.router)
app.include_router(bp_u8.router)
app.include_router(bp_user.router)
app.include_router(bp_yostar.router)
app.include_router(legacy_bp.router)
app.include_router(misc_bp.router)


def main():
    uvicorn.run(
        "openbachelors.app:app",
        host="127.0.0.1",
        port=8443,
        reload=True,
    )


if __name__ == "__main__":
    main()
