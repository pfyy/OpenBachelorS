from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator

bp_shop = Blueprint("bp_shop", __name__)


@bp_shop.route("/shop/getSkinGoodList", methods=["POST"])
@player_data_decorator
def shop_getSkinGoodList(player_data):
    request_json = request.get_json()
    response = {}
    return response
