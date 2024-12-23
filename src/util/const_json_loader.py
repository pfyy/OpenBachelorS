import os
from pathlib import Path
import json
from copy import deepcopy


class ConstJson:
    def __init__(self, json_obj):
        self.json_obj = json_obj

    def __getitem__(self, key):
        child_json_obj = self.json_obj[key]
        if isinstance(child_json_obj, dict) or isinstance(child_json_obj, list):
            child_const_json = ConstJson(child_json_obj)
            return child_const_json
        return child_json_obj

    def copy(self):
        return deepcopy(self.json_obj)


class ConstJsonLoader:
    TARGET_DIR_LST = ["conf", "res/excel"]

    def __init__(self):
        self.const_json_dict = {}
        for target_dir in self.TARGET_DIR_LST:
            for root, dirs, files in os.walk(target_dir):
                for name in files:
                    if name.endswith(".json"):
                        filepath = Path(os.path.join(root, name)).as_posix()
                        with open(filepath, encoding="utf-8") as f:
                            json_obj = json.load(f)
                        const_json = ConstJson(json_obj)
                        self.const_json_dict[filepath] = const_json

    def __getitem__(self, key):
        return self.const_json_dict[key]


const_json_loader = ConstJsonLoader()
