# Copyright 2021 iiPython

# Modules
import os
import json
from .utils.logging import logger

# Config class
class Configuration(object):
    def __init__(self) -> None:
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not os.path.exists("config.json"):
            return logger.log("crash", "No config.json file exists, please create it and relaunch.")

        with open("config.json", "r") as config_file:
            try:
                raw_config = json.loads(config_file.read())

            except json.JSONDecodeError:
                return logger.log("crash", "Failed while attempting to load config.json")

        return raw_config

    def get(self, key: any) -> any:
        if key not in self.config:
            raise KeyError

        return self.config[key]

# Initialization
config = Configuration()
