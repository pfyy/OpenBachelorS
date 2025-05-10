import os
import json

from psycopg.types.json import Json

from ..const.json_const import true, false, null
from .db_manager import IS_DB_READY, get_db_conn, create_user_if_necessary


class BasicExtraSave:
    @classmethod
    def get_default_save_obj(cls):
        return {
            "received_mail_lst": [],
            "removed_mail_lst": [],
            "received_message_lst": [],
        }

    def reset(self):
        self.save_obj = ExtraSave.get_default_save_obj()


class ExtraSave(BasicExtraSave):
    def __init__(self, filepath: str):
        self.filepath = filepath

        if os.path.isfile(self.filepath):
            with open(self.filepath, encoding="utf-8") as f:
                self.save_obj = json.load(f)
        else:
            self.save_obj = ExtraSave.get_default_save_obj()

    def save(self):
        dirpath = os.path.dirname(self.filepath)
        os.makedirs(dirpath, exist_ok=True)

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.save_obj, f, ensure_ascii=False, indent=4)


class DBExtraSave(BasicExtraSave):
    def __init__(self, username: str):
        self.username = username

        create_user_if_necessary(self.username)

        save_obj = self.load_save_obj_from_db()
        if not save_obj:
            save_obj = ExtraSave.get_default_save_obj()

        self.save_obj = save_obj

    def load_save_obj_from_db(self):
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT extra FROM player_data WHERE username = %s",
                    (self.username,),
                )
                return cur.fetchone()[0]

    def save(self):
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE player_data SET extra = %s WHERE username = %s",
                    (
                        Json(self.save_obj),
                        self.username,
                    ),
                )
                conn.commit()
