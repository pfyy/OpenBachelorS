import json

from fastapi import APIRouter
from fastapi import Request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.helper import get_username_by_token
from ..util.player_data import player_data_decorator


router = APIRouter()


@router.post("/user/auth/v1/token_by_phone_password")
@router.post("/user/auth/v2/token_by_phone_code")
async def user_auth_v1_token_by_phone_password(request: Request):
    request_json = await request.json()

    phone = request_json["phone"]

    response = {"data": {"token": phone}, "msg": "OK", "status": 0, "type": "A"}
    return response


@router.get("/user/info/v1/basic")
async def user_info_v1_basic(request: Request):
    token = request.query_params.get("token", "")
    username = get_username_by_token(token)
    response = {
        "data": {
            "hgId": "123456789",
            "phone": username,
            "email": null,
            "identityNum": "123456789",
            "identityName": "123456789",
            "isMinor": false,
            "isLatestUserAgreement": true,
        },
        "msg": "OK",
        "status": 0,
        "type": "A",
    }
    return response


@router.post("/user/oauth2/v2/grant")
async def user_oauth2_v2_grant(request: Request):
    request_json = await request.json()

    token = request_json["token"]

    response = {
        "data": {"uid": "123456789", "code": token},
        "msg": "OK",
        "status": 0,
        "type": "A",
    }
    return response


@router.post("/user/online/v1/loginout")
async def user_online_v1_loginout(request: Request):
    request_json = await request.json()

    response = {"msg": "OK", "status": 0, "type": "A"}
    return response


@router.post("/user/info/v1/logout")
async def user_info_v1_logout(request: Request):
    request_json = await request.json()

    response = {"msg": "OK", "status": 0, "type": "A"}
    return response


@router.post("/user/info/v1/update_agreement")
async def user_info_v1_update_agreement(request: Request):
    request_json = await request.json()

    response = {"msg": "OK", "status": 0, "type": "A"}
    return response


@router.post("/user/changeAvatar")
@player_data_decorator
async def user_changeAvatar(player_data, request: Request):
    request_json = await request.json()

    avatar = request_json

    player_data["status"]["avatar"] = avatar

    response = {}
    return response


@router.post("/user/changeResume")
@player_data_decorator
async def user_changeResume(player_data, request: Request):
    request_json = await request.json()

    resume = request_json["resume"]

    player_data["status"]["resume"] = resume

    response = {}
    return response


@router.post("/user/login")
@router.post("/user/quick-login")
@router.post("/user/detail")
async def user_login(request: Request):
    request_json = await request.json()

    token = request_json.get("Token", "")

    if not token:
        authorization_obj = json.loads(request.headers.get("Authorization"))
        token = authorization_obj["Head"]["Token"]

    username = get_username_by_token(token)

    response = {
        "Code": 200,
        "Data": {
            "AgeVerifyMethod": 0,
            "IsNew": 0,
            "Destroy": null,
            "IsTestAccount": false,
            "Keys": [
                {
                    "ID": "123456789",
                    "Type": "yostar",
                    "Key": "123456789",
                    "NickName": username,
                    "CreatedAt": 1700000000,
                }
            ],
            "ServerNowAt": 1700000000,
            "UserInfo": {
                "ID": "123456789",
                "UID2": 0,
                "PID": "US-ARKNIGHTS",
                "Token": token,
                "Birthday": "",
                "RegChannel": "googleplay",
                "TransCode": "",
                "State": 1,
                "DeviceID": "",
                "CreatedAt": 1700000000,
            },
            "Yostar": {
                "ID": "123456789",
                "Country": "US",
                "Nickname": "Bachelor",
                "Picture": "",
                "State": 1,
                "AgreeAd": 0,
                "CreatedAt": 1700000000,
            },
        },
        "Msg": "OK",
    }
    return response


@router.post("/user/agreement/confirm")
async def user_agreement_confirm(request: Request):
    request_json = await request.json()

    response = {"Code": 200, "Data": {}, "Msg": "OK"}
    return response


@router.post("/user/useRenameCard")
@player_data_decorator
async def user_useRenameCard(player_data, request: Request):
    request_json = await request.json()

    player_data["status"]["nickName"] = request_json["nickName"]

    response = {
        "result": 0,
    }
    return response
