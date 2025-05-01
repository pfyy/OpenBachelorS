import time

FAKETIME = 1747296000


def faketime():
    t = time.time()

    if FAKETIME > 0:
        t = FAKETIME + t % (24 * 60 * 60)

    return t
