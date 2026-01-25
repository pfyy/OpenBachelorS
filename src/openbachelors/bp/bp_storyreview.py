from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

router = APIRouter()


@router.post("/storyreview/readStory")
@player_data_decorator
async def storyreview_readStory(player_data, request: Request):
    request_json = await request.json()
    response = {"readCount": 0}
    return response


@router.post("/story/finishStory")
@player_data_decorator
async def story_finishStory(player_data, request: Request):
    request_json = await request.json()
    response = {"items": []}
    return response
