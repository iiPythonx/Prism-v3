# Copyright 2021 iiPython

# Modules
import os
from prism.config import config
from discord.ext import commands
from ..utils.logging import logger

# Bot class
class PrismBot(commands.Bot):
    def __init__(self, **kwargs) -> None:
        super().__init__(command_prefix = config.get("prefix"), **kwargs)

        # Initialize logging
        self.logger = logger
        self.log = logger.log

        # Handle post-initialization
        self.remove_command("help")

    def launch_bot(self) -> None:
        self.log("info", "Launching bot...")

        # Grab token
        token = os.getenv("TOKEN")
        if not token:
            return self.log("crash", "No token environment variable exists.")

        # Launch bot
        self.run(token, reconnect = True)

    # Main events
    async def on_ready(self) -> None:
        self.log("success", "Logged in as {}.".format(str(self.user)))
