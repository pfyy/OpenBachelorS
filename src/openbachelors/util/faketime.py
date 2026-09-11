import time
from datetime import datetime, timezone, timedelta

from .const_json_loader import const_json_loader
from ..const.filepath import CONFIG_JSON

FAKETIME = const_json_loader[CONFIG_JSON]["faketime"]


def faketime():
    dt = datetime.fromtimestamp(1777123800, tz=timezone(timedelta(hours=8)))

    target_dt = dt.replace(hour=4, minute=0, second=1, microsecond=0)

    if dt >= target_dt:
        target_dt += timedelta(days=1)

    return target_dt.timestamp()

    t = time.time()

    if FAKETIME > 0:
        t = FAKETIME + t % (24 * 60 * 60)

    return t
