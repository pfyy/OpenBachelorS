from ..const.filepath import MAIL_JSON
from ..util.const_json_loader import const_json_loader


def get_player_mailbox(player_data):
    received_mail_set = set(player_data.extra_save.save_obj["received_mail_lst"])
    removed_mail_set = set(player_data.extra_save.save_obj["removed_mail_lst"])

    mail_json_obj = const_json_loader[MAIL_JSON].copy()

    pending_mail_set = set()
    dst_mail_lst = []

    for mail in mail_json_obj["mailList"]:
        mail_id = mail["mailId"]

        if mail_id in removed_mail_set:
            continue

        if mail_id in received_mail_set:
            mail["state"] = 1
        else:
            pending_mail_set.add(mail_id)

        dst_mail_lst.append(mail)

    mail_json_obj["mailList"] = dst_mail_lst

    return mail_json_obj, pending_mail_set
