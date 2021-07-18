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
        self.emojis = {
            "checkmark": ":white_check_mark:"
        }

    def embed(self, **kwargs) -> discord.Embed:
        if "color" not in kwargs:
            kwargs["color"] = 0xEB8F6B

        embed = discord.Embed(**kwargs)
        if "footer" in kwargs:
            author = kwargs["footer"].author
            embed.set_footer(icon_url = author.avatar_url, text = f"| Requested by {author}.")

        return embed

    def small_embed(self, message: str, **kwargs) -> discord.Embed:
        return self.embed(description = f"**{message}**", **kwargs)

    def error(self, message: str, syserror: bool = False) -> discord.Embed:
        return self.small_embed({False: ":no_entry_sign:", True: ":interrobang:"}[syserror] + f" {message}", color = 0xd9534f)

    def noacc(self, ctx: commands.Context, user: Union[discord.User, discord.Member] = None) -> discord.Embed:
        return self.error(f"""{"You don't" if user is None or user is not None and user == ctx.author else f"{user.name} doesn't"} have a Prism account{f" (`{ctx.prefix}create` to make one)" if user is None else ""}.""")

    def locate_module(self, command: str) -> Union[str, None]:
        path = config.get("cmd_path")
        for path, _, files in os.walk(path):
            for file in files:
                if file.split(".py")[0] == command:
                    relpath = os.path.join(path, file).replace("\\", "/")  # Convert to unix-like path
                    modpath = relpath[:-3].replace("/", ".")  # Convert to Python dot-path
                    return modpath

    def format_coins(self, amount: int) -> str:
        return "{:20,}".format(amount)

    def format_list(self, list_to_format: list) -> str:
        return "".join(_ + ", " for _ in list_to_format)[:-2]

    def frmt_name(self, user: Union[discord.User, discord.Member]) -> str:
        return user.name if not hasattr(user, "nick") or hasattr(user, "nick") and user.nick is None else user.nick

    def scale_size(self, bytes: int, suffix: str = "B", add_suffix: bool = True) -> str:
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit if add_suffix else ''}{suffix if add_suffix else ''}"

            bytes /= factor
