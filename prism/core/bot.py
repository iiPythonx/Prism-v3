# Copyright 2021 iiPython
# Prism Internal Engine

# Modules
import os
import asyncio
import secrets
import discord
import iipython as ip

from .utils import Utils
from typing import Union
from ..logging import logger
from ..database import Database
from prism.config import config
from discord.ext import commands

# Bot class
class PrismBot(commands.Bot):
    def __init__(self, intents: Union[discord.Intents, None] = None, **kwargs) -> None:
        if intents is None:
            intents = discord.Intents.default()
            intents.members = True

        super().__init__(
            intents = intents,
            help_command = None,
            **kwargs
        )

        # Initialize logging
        self.logger = logger
        self.log = logger.log

        # Load core
        self.db = Database()
        self.core = Utils(self)

        self.config = config
        self.cooldowns = self.core.cooldowns

        self.owner = config.get(["admins", "owner"])

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
        tid = self.core.timer.start()
        if cmd_path is None:
            try:
                cmd_path = config.get(["paths", "cmd_path"])

            except IndexError:
                pass

        if not cmd_path:
            return self.log("crash", "No command directory specified to load from.")

        elif not os.path.exists(cmd_path):
            return self.log("crash", "Command directory does not exist.")

        self.core.storage["cmd_path"] = cmd_path

        # Load commands
        for path, _, files in os.walk(cmd_path):
            for file in files:
                if not file.endswith(".py"):
                    continue  # Ignore __pycache__ and etc

                cmd_path = os.path.join(path, file)
                relpath = cmd_path.replace("\\", "/").replace(os.getcwd().replace("\\", "/"), "").lstrip("/")  # Convert to unix-like path
                modpath = relpath[:-3].replace("/", ".")  # Convert to Python dot-path

                self.load_extension(modpath)

        self.log("success", "Loaded commands in {} second(s).".format(self.core.timer.end(tid)))

    # Main events
    async def on_ready(self) -> None:
        self.log("success", "Logged in as {}.".format(str(self.user)))

    async def on_application_command_error(self, ctx: commands.Context, error: Exception) -> any:
        error_map = {
            commands.BadUnionArgument: lambda e: "Invalid arguments provided.",
            commands.MemberNotFound: lambda e: "No such user exists.",
            commands.MissingPermissions: lambda e: "You need the following permissions to run this:\n" + ", ".join([_ for _ in " ".join(e.replace(",", "").split(" ")[3:][:-5]).split(" and ")]),
            commands.NSFWChannelRequired: lambda e: "This command only works in NSFW channels."
        }
        if type(error) in error_map:
            return await ctx.send(embed = self.core.error(error_map[type(error)](str(error))))

        error_code = secrets.token_hex(8)
        self.log("error", f"{error_code} | {ctx.command} | {type(error).__name__}: {error}")

        return await ctx.send(
            embed = self.core.error(
                f"An unexpected error has occured, please report this to {self.owner}.\nError code: `{error_code}`",
                syserror = True
            )
        )
