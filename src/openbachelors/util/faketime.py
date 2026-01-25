import time

from .const_json_loader import const_json_loader
from ..const.filepath import CONFIG_JSON

FAKETIME = const_json_loader[CONFIG_JSON]["faketime"]


def faketime():
    t = time.time()

    if FAKETIME > 0:
        t = FAKETIME + t % (24 * 60 * 60)

    return t
