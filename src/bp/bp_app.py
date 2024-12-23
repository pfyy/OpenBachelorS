from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader


bp_app = Blueprint("bp_app", __name__)


@bp_app.route("/app/v1/config")
def app_v1_config():
    host = const_json_loader[CONFIG_JSON]["host"]
    port = const_json_loader[CONFIG_JSON]["port"]
    url = f"http://{host}:{port}"

    response = {
        "data": {
            "antiAddiction": {"minorPeriodEnd": 21, "minorPeriodStart": 20},
            "payment": [
                {"key": "alipay", "recommend": true},
                {"key": "wechat", "recommend": false},
                {"key": "pcredit", "recommend": false},
            ],
            "customerServiceUrl": f"{url}/chat/h5/v2/index.html?sysnum=889ee281e3564ddf883942fe85764d44&channelid=2",
            "cancelDeactivateUrl": f"{url}/cancellation",
            "agreementUrl": {
                "game": f"{url}/protocol/plain/ak/index",
                "unbind": f"{url}/protocol/plain/ak/cancellation",
                "gameService": f"{url}/protocol/plain/ak/service",
                "account": f"{url}/protocol/plain/index",
                "privacy": f"{url}/protocol/plain/privacy",
                "register": f"{url}/protocol/plain/registration",
                "updateOverview": f"{url}/protocol/plain/overview_of_changes",
                "childrenPrivacy": f"{url}/protocol/plain/children_privacy",
            },
            "app": {
                "enablePayment": true,
                "enableAutoLogin": false,
                "enableAuthenticate": true,
                "enableAntiAddiction": true,
                "enableUnbindGrant": true,
                "wechatAppId": "wx0ae7fb63d830f7c1",
                "alipayAppId": "2018091261385264",
                "oneLoginAppId": "7af226e84f13f17bd256eca8e1e61b5a",
                "enablePaidApp": false,
                "appName": "明日方舟",
                "appAmount": 600,
                "needShowName": false,
                "customerServiceUrl": f"{url}/ak?hg_token={{hg_token}}&source_from=sdk",
                "needAntiAddictionAlert": true,
                "enableScanLogin": false,
            },
            "scanUrl": {"login": "hypergryph://scan_login"},
            "userCenterUrl": f"{url}/pcSdk/userInfo",
        },
        "msg": "OK",
        "status": 0,
        "type": "A",
    }
    return response
