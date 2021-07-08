# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands

# Utility class
class Utils(object):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def embed(self, **kwargs) -> discord.Embed:
        if "color" not in kwargs:
            kwargs["color"] = 0xEB8F6B

        return discord.Embed(**kwargs)

    def error(self, message: str) -> discord.Embed:
        return self.embed(description = f"**{message}**", color = 0xd9534f)

    def noacc(self, ctx: commands.Context) -> discord.Embed:
        return self.error(f"You don't have a Prism account (`{ctx.prefix}create` to make one).")
