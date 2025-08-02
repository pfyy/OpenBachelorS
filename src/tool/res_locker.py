import datetime

from ..const.filepath import RES_LOCK_FILEPATH


if __name__ == "__main__":
    t = int(
        datetime.datetime.combine(datetime.date.today(), datetime.time.max).timestamp()
    )
    with open(RES_LOCK_FILEPATH, "w", encoding="utf-8") as f:
        f.write(str(t))
