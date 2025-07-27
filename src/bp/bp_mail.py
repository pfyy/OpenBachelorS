from flask import Blueprint
from flask import request

from ..const.json_const import true, false, null
from ..const.filepath import CONFIG_JSON, VERSION_JSON, DISPLAY_META_TABLE
from ..util.const_json_loader import const_json_loader
from ..util.player_data import player_data_decorator
from ..util.mail_helper import get_player_mailbox

bp_mail = Blueprint("bp_mail", __name__)


@bp_mail.route("/mail/getMetaInfoList", methods=["POST"])
@player_data_decorator
def mail_getMetaInfoList(player_data):
    request_json = request.get_json()

    mail_json_obj, pending_mail_set = get_player_mailbox(player_data)

    result_lst = []

    for mail in mail_json_obj["mailList"]:
        result_lst.append(
            {
                "mailId": mail["mailId"],
                "createAt": mail["createAt"],
                "state": mail["state"],
                "hasItem": mail["hasItem"],
                "type": mail["type"],
            }
        )

    player_data["pushFlags"]["hasGifts"] = int(bool(pending_mail_set))

    response = {"result": result_lst}
    return response


@bp_mail.route("/mail/listMailBox", methods=["POST"])
@player_data_decorator
def mail_listMailBox(player_data):
    request_json = request.get_json()

    mail_json_obj, pending_mail_set = get_player_mailbox(player_data)

    player_data["pushFlags"]["hasGifts"] = int(bool(pending_mail_set))

    response = mail_json_obj
    return response


def get_item_lst(mail_json_obj, mail_id_set):
    item_lst = []

    for mail in mail_json_obj["mailList"]:
        if mail["mailId"] in mail_id_set:
            item_lst += mail["items"]

    return item_lst


@bp_mail.route("/mail/receiveMail", methods=["POST"])
@player_data_decorator
def mail_receiveMail(player_data):
    request_json = request.get_json()

    mail_json_obj, pending_mail_set = get_player_mailbox(player_data)

    mail_id = request_json["mailId"]
    player_data.extra_save.save_obj["received_mail_lst"].append(mail_id)

    item_lst = get_item_lst(mail_json_obj, {mail_id})

    pending_mail_set.remove(mail_id)

    player_data["pushFlags"]["hasGifts"] = int(bool(pending_mail_set))

    response = {
        "result": 0,
        "items": item_lst,
    }
    return response


@bp_mail.route("/mail/receiveAllMail", methods=["POST"])
@player_data_decorator
def mail_receiveAllMail(player_data):
    request_json = request.get_json()

    mail_json_obj, pending_mail_set = get_player_mailbox(player_data)

    for mail_id in pending_mail_set:
        player_data.extra_save.save_obj["received_mail_lst"].append(mail_id)

    item_lst = get_item_lst(mail_json_obj, pending_mail_set)

    pending_mail_set = set()

    player_data["pushFlags"]["hasGifts"] = int(bool(pending_mail_set))

    response = {
        "items": item_lst,
    }
    return response


@bp_mail.route("/mail/removeAllReceivedMail", methods=["POST"])
@player_data_decorator
def mail_removeAllReceivedMail(player_data):
    request_json = request.get_json()

    player_data.extra_save.save_obj["removed_mail_lst"] += (
        player_data.extra_save.save_obj["received_mail_lst"]
    )
    player_data.extra_save.save_obj["received_mail_lst"] = []

    response = {}
    return response


@bp_mail.route("/mailCollection/getList", methods=["POST"])
@player_data_decorator
def mailCollection_getList(player_data):
    request_json = request.get_json()

    display_meta_table = const_json_loader[DISPLAY_META_TABLE]

    collection_lst = []

    for i, _ in display_meta_table["mailArchiveData"]["mailArchiveInfoDict"]:
        collection_lst.append(i)

    response = {
        "collections": collection_lst,
        "extra": [],
    }
    return response
