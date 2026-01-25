import os
from pathlib import Path
import json
from copy import deepcopy
from abc import ABC, abstractmethod
from functools import wraps

from ..const.filepath import RES_EXCEL_DIRPATH


class SavableThing(ABC):
    @abstractmethod
    async def save(self):
        pass

    @abstractmethod
    def reset(self):
        pass


class ConstJsonLike(ABC):
    @abstractmethod
    def __contains__(self, key):
        pass

    @abstractmethod
    def __getitem__(self, key):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def copy(self):
        pass


# always a dict-like/list-like object
class ConstJson(ConstJsonLike):
    def __init__(self, json_obj):
        self.json_obj = json_obj
        self.is_dict = isinstance(json_obj, dict)

    def __contains__(self, key):
        if self.is_dict:
            return key in self.json_obj
        raise TypeError

    def __getitem__(self, key):
        child_json_obj = self.json_obj[key]
        if isinstance(child_json_obj, dict) or isinstance(child_json_obj, list):
            child_const_json = ConstJson(child_json_obj)
            return child_const_json
        return child_json_obj

    def __iter__(self):
        if self.is_dict:
            for key in self.json_obj:
                yield key, self[key]
        else:
            for i in range(len(self.json_obj)):
                yield i, self[i]

    def __len__(self):
        return len(self.json_obj)

    def copy(self):
        return deepcopy(self.json_obj)


def lazy_loaded_const_json_decorator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.loaded:
            self.load_json_obj()

        return func(self, *args, **kwargs)

    return wrapper


class LazyLoadedConstJson(ConstJson):
    def __init__(self, filepath):
        self.filepath = filepath
        self.loaded = False

    def load_json_obj(self):
        with open(self.filepath, encoding="utf-8") as f:
            json_obj = json.load(f)

        super().__init__(json_obj)
        self.loaded = True

    @lazy_loaded_const_json_decorator
    def __contains__(self, key):
        return super().__contains__(key)

    @lazy_loaded_const_json_decorator
    def __getitem__(self, key):
        return super().__getitem__(key)

    @lazy_loaded_const_json_decorator
    def __iter__(self):
        return super().__iter__()

    @lazy_loaded_const_json_decorator
    def __len__(self):
        return super().__len__()

    @lazy_loaded_const_json_decorator
    def copy(self):
        return super().copy()


class ConstJsonLoader:
    TARGET_DIR_LST = ["conf", "data", RES_EXCEL_DIRPATH]

    def __init__(self):
        self.const_json_dict = {}
        for target_dir in self.TARGET_DIR_LST:
            for root, dirs, files in os.walk(target_dir):
                for name in files:
                    if name.endswith(".json"):
                        filepath = Path(os.path.join(root, name)).as_posix()
                        const_json = LazyLoadedConstJson(filepath)
                        self.const_json_dict[filepath] = const_json

    def __getitem__(self, key):
        return self.const_json_dict[key]


const_json_loader = ConstJsonLoader()
