# Copyright 2021 iiPython

# Modules
import sys
from rich.console import Console

# Logging class
rcon = Console()
class Logging(object):
    def __init__(self) -> None:
        self._color_map = {"success": "green", "info": "cyan", "warn": "yellow", "error": "red", "crash": "red"}

    def log(self, log_type: str, message: str, exit_code: int = None) -> None:
        if log_type not in self._color_map:
            raise ValueError("no such log level: '{}'".format(log_type))

        rcon.log("[{}][{}] {}".format(self._color_map[log_type], log_type.upper(), message))
        if log_type == "crash":
            sys.exit(exit_code if exit_code is not None else 1)

        elif exit_code is not None:
            sys.exit(exit_code)

# Initialization
logger = Logging()
