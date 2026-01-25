import json
import logging

from ..const.filepath import CONFIG_JSON, VERSION_JSON
from .const_json_loader import const_json_loader
from .helper import decode_battle_log
from .log_helper import IS_DEBUG


logger = logging.getLogger(__name__)


def log_battle_log_if_necessary(player_data, raw_data):
    if IS_DEBUG:
        try:
            decoded_battle_log = decode_battle_log(player_data, raw_data)
            decoded_battle_log_str = json.dumps(decoded_battle_log, ensure_ascii=False)
        except Exception:
            decoded_battle_log_str = "failed to decode battle log"

        logger.debug(decoded_battle_log_str)
