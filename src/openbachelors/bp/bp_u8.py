import json

from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.server_url import get_server_url


router = APIRouter()


@router.post("/u8/user/v1/getToken")
async def u8_user_v1_getToken(request: Request):
    request_json = await request.json()
    extension_obj = json.loads(request_json["extension"])
    if "code" in extension_obj:
        code = extension_obj["code"]
    elif "token" in extension_obj:
        code = extension_obj["token"]
    else:
        code = ""

    response = {
        "result": 0,
        "captcha": {},
        "error": "",
        "uid": "1",
        "channelUid": "123456789",
        "token": code,
        "isGuest": 0,
        "extension": '{"isAuthenticate":true,"isMinor":false}',
    }
    return response


@router.post("/u8/pay/getAllProductList")
async def u8_pay_getAllProductList(request: Request):
    response = {"productList": []}
    return response


@router.post("/u8/user/auth/v1/agreement_version")
@router.get("/u8/user/auth/v1/agreement_version")
async def u8_user_auth_v1_agreement_version(request: Request):
    url = get_server_url(request)

    response = {
        "data": {
            "agreementUrl": {
                "childrenPrivacy": f"{url}/protocol/plain/ak/children_privacy",
                "privacy": f"{url}/protocol/plain/ak/privacy",
                "service": f"{url}/protocol/plain/ak/service",
                "updateOverview": f"{url}/protocol/plain/ak/overview_of_changes",
            },
            "authorized": true,
            "isLatestUserAgreement": true,
        },
        "msg": "OK",
        "status": 0,
        "type": "",
    }
    return response


@router.post("/u8/user/auth/v1/update_agreement")
async def u8_user_auth_v1_update_agreement(request: Request):
    request_json = await request.json()

    response = {"msg": "OK", "status": 0, "type": ""}
    return response
