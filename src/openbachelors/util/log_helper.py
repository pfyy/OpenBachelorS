import os

from .const_json_loader import const_json_loader
from ..const.filepath import CONFIG_JSON


IS_DEBUG = "PROD_FLAG" not in os.environ and const_json_loader[CONFIG_JSON]["debug"]
