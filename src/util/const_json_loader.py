import os
from pathlib import Path
import json
from copy import deepcopy


class ConstJsonIter:
    def __init__(self, const_json):
        self.const_json = const_json

        self.iter_lst_idx = 0
        if isinstance(const_json.json_obj, dict):
            self.iter_lst = list(const_json.json_obj.keys())
        elif isinstance(const_json.json_obj, list):
            self.iter_lst = list(range(len(const_json.json_obj)))
        else:
            raise TypeError

    def __next__(self):
        if self.iter_lst_idx >= len(self.iter_lst):
            raise StopIteration
        key = self.iter_lst[self.iter_lst_idx]
        self.iter_lst_idx += 1
        return key, self.const_json[key]


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

    def __iter__(self):
        const_json_iter = ConstJsonIter(self)
        return const_json_iter

    def __contains__(self, key):
        if isinstance(self.json_obj, dict):
            return key in self.json_obj
        raise TypeError

    def __len__(self):
        return len(self.json_obj)


class ConstJsonLoader:
    TARGET_DIR_LST = ["conf", "res/excel", "data"]

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
