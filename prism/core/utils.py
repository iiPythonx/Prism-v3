# Copyright 2021 iiPython

# Modules
import os
import discord
from typing import Union
from prism.config import config
from discord.ext import commands

# Utility class
class Utils(object):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def embed(self, **kwargs) -> discord.Embed:
        if "color" not in kwargs:
            kwargs["color"] = 0xEB8F6B

        return discord.Embed(**kwargs)

    def small_embed(self, message: str, **kwargs) -> discord.Embed:
        return self.embed(description = f"**{message}**", **kwargs)

    def error(self, message: str, syserror: bool = False) -> discord.Embed:
        return self.small_embed({False: ":no_entry_sign:", True: ":interrobang:"}[syserror] + f" {message}", color = 0xd9534f)

    def noacc(self, ctx: commands.Context) -> discord.Embed:
        return self.error(f"You don't have a Prism account (`{ctx.prefix}create` to make one).")

    def locate_module(self, command: str) -> Union[str, None]:
        path = config.get("cmd_path")
        for path, _, files in os.walk(path):
            for file in files:
                if file.split(".py")[0] == command:
                    relpath = os.path.join(path, file).replace("\\", "/")  # Convert to unix-like path
                    modpath = relpath[:-3].replace("/", ".")  # Convert to Python dot-path
                    return modpath
