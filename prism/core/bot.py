# Copyright 2021 iiPython

# Modules
import os
import secrets
from .utils import Utils
from ..database import Database
from prism.config import config
from discord.ext import commands
import prism.utils.objects as obj
from ..utils import (timer, logger, Cooldowns)

# Bot class
class PrismBot(commands.Bot):
    def __init__(self, **kwargs) -> None:
        super().__init__(command_prefix = config.get("prefix"), **kwargs)
        self.config = config

        # Initialize logging
        self.logger = logger
        self.log = logger.log

        # Load core
        self.db = Database()
        self.core = Utils(self)
        self.cooldowns = Cooldowns(self)
        self.objects = obj.map

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
        tid = timer.start()
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
        self.log("success", "Loaded commands in {} second(s).".format(timer.end(tid)))

    # Main events
    async def on_ready(self) -> None:
        self.log("success", "Logged in as {}.".format(str(self.user)))

    async def on_command_error(self, ctx: commands.Context, error: Exception) -> any:
        error_map = {
            commands.CommandNotFound: "No command with that name exists."
        }
        if type(error) in error_map:
            return await ctx.send(embed = self.core.error(error_map[type(error)]))

        error_code = secrets.token_hex(8)
        self.log("error", f"{error_code} | {ctx.command} | {error}")

        return await ctx.send(
            embed = self.core.error(
                f"An unexpected error has occured, please report this to {config.get('owner')}.\nError code: `{error_code}`",
                syserror = True
            )
        )
