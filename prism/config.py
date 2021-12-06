# Copyright 2021-xx iiPython

# Modules
import os
import json
from typing import Any
from .logging import logger

# Config class
class Configuration(object):
    def __init__(self) -> None:
        self.default = {
            "debug": False
        }
        self.config = self.default | self._load_config()

    def _load_config(self) -> dict:
        if not os.path.exists("config.json"):
            return logger.log("crash", "No config.json file exists, please create it and relaunch.")

        with open("config.json", "r") as config_file:
            try:
                raw_config = json.loads(config_file.read())

            except json.JSONDecodeError:
                return logger.log("crash", "Failed while attempting to load config.json")

        return raw_config

    def get(self, key: Any) -> Any:
        if isinstance(key, list):
            value = self.config[key[0]]
            for k in key[1:]:
                value = value[k]

        else:
            value = self.config[key]

        return value

    def set(self, key: Any, value: Any) -> None:
        self.config[key] = value

    def merge(self, data: dict) -> None:
        self.config = self.config | data

# Initialization
config = Configuration()
