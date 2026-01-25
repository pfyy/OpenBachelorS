import logging
from .util.log_helper import IS_DEBUG


if IS_DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
