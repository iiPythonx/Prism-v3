# Copyright 2021 iiPython

# Modules
import os
from .utils import Utils
from ..utils.timer import timer
from prism.config import config
from discord.ext import commands
from ..utils.logging import logger

# Bot class
class PrismBot(commands.Bot):
    def __init__(self, **kwargs) -> None:
        super().__init__(command_prefix = config.get("prefix"), **kwargs)
        self.config = config

        # Initialize logging
        self.logger = logger
        self.log = logger.log

        # Load core
        self.core = Utils(self)

        # Handle post-initialization
        self.remove_command("help")

    def launch_bot(self) -> None:
        self.log("info", "Launching bot...")

        # Grab token
        token = os.getenv("TOKEN")
        if not token:
            return self.log("crash", "No token environment variable exists.")

        # Load commands
        self.load_cmds()

        # Launch bot
        self.run(token, reconnect = True)

    def load_cmds(self, cmd_path: str = None) -> None:
        timer.start("cmdload")
        if "cmd_path" in config.config and cmd_path is None:
            cmd_path = config.get("cmd_path")

        if not cmd_path:
            return self.log("crash", "No command directory specified to load from.")

        elif not os.path.exists(cmd_path):
            return self.log("crash", "Command directory does not exist.")

        # Load commands
        for path, _, files in os.walk(cmd_path):
            for file in files:
                if not file.endswith(".py"):
                    continue  # Ignore __pycache__ and etc

                relpath = os.path.join(path, file).replace("\\", "/")  # Convert to unix-like path
                modpath = relpath[:-3].replace("/", ".")  # Convert to Python dot-path

                # Load command
                self.load_extension(modpath)

        # Log
        self.log("success", "Loaded commands in {} second(s).".format(timer.end("cmdload")))

    # Main events
    async def on_ready(self) -> None:
        self.log("success", "Logged in as {}.".format(str(self.user)))
