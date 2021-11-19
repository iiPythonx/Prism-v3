# Copyright 2021 iiPython

# Modules
import os
import discord
import subprocess
from shutil import which
from typing import Union
from discord.ext import commands

from .modules.timer import timer
from .modules.images import images
from .modules.cooldowns import Cooldowns
from .modules.inventory import Inventory

# Data directory
class PrismDataDirectory(object):
    def __init__(self, dir_: str) -> None:
        self.dir = dir_

    def path(self, path: str) -> str:
        return os.path.join(self.dir, path)

# Utility class
class Utils(object):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.emojis = {"checkmark": ":white_check_mark:"}
        self.storage = {"accent": "#EB8F6B"}

        self.asset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets"))

        # Modules
        self.timer = timer
        self.images = images
        self.inventory = Inventory
        self.cooldowns = Cooldowns(self)

    def color(self, hex_: str, accent_def: bool = True) -> discord.Color:
        try:
            return discord.Color.from_hex(hex_)

        except Exception:
            return self.color(self.storage["accent"])

    def embed(self, footer = None, **kwargs) -> discord.Embed:
        if "color" not in kwargs:
            kwargs["color"] = self.color(self.storage["accent"])

        embed = discord.Embed(**kwargs)
        if footer is not None:
            author = footer.author
            embed.set_footer(icon_url = author.avatar.url, text = f"Requested by {author}.")

        return embed

    def small_embed(self, message: str, **kwargs) -> discord.Embed:
        return self.embed(description = f"**{message}**", **kwargs)

    def error(self, message: str, syserror: bool = False) -> discord.Embed:
        return self.small_embed({False: ":no_entry_sign:", True: ":interrobang:"}[syserror] + f" {message}", color = 0xd9534f)

    def noacc(self, ctx: commands.Context, user: Union[discord.User, discord.Member] = None) -> discord.Embed:
        return self.error(f"""{"You don't" if user is None or user is not None and user == ctx.author else f"{user.name} doesn't"} have a Prism account{f" (`{ctx.prefix}create` to make one)" if user is None else ""}.""")

    def nouser(self) -> discord.Embed:
        return self.error("No such user was found.")

    def locate_module(self, command: str) -> Union[str, None]:
        path = self.storage.get("cmd_path", None)
        if path is None:
            return None

        for path, _, files in os.walk(path):
            for file in files:
                if file.split(".py")[0] == command:
                    relpath = os.path.join(path, file).replace("\\", "/")  # Convert to unix-like path
                    modpath = relpath[:-3].replace("/", ".")  # Convert to Python dot-path
                    return modpath

    def format_coins(self, amount: int) -> str:
        return "{:20,}".format(round(amount)).strip()

    def format_list(self, list_to_format: list) -> str:
        return ", ".join(list_to_format)

    def frmt_name(self, user: discord.Member) -> str:
        return user.name if not hasattr(user, "nick") or hasattr(user, "nick") and user.nick is None else user.nick

    def scale_size(self, bytes: int, suffix: str = "B", add_suffix: bool = True) -> str:
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit if add_suffix else ''}{suffix if add_suffix else ''}"

            bytes /= factor

    def fetch_output(self, command: Union[str, list], split: tuple = None) -> str:
        base = command.split(" ")[0] if isinstance(command, str) else command[0].split(" ")[0]
        if not which(base):
            return "N/A"

        if isinstance(command, str):
            command = command.split(" ")

        st = subprocess.run(command, stdout = subprocess.PIPE)
        result = st.stdout.decode("UTF-8")
        if split is not None:
            result = result.split(split[0])[split[1]]

        return result.rstrip("\n")

    def amountstr_to_bal(self, amount: str, balance: int) -> int:
        funcs = {
            "all": lambda b: b,
            "max": lambda b: b,
            "half": lambda b: round(b / 2)
        }
        amount = amount.lower()
        if amount in funcs:
            return funcs[amount](balance)

        elif amount.endswith("%"):
            if len(amount) > 4 or len(amount) < 2:
                raise ValueError("Invalid percent specified.")

            try:
                percent = int(amount[:-1])
                if percent > 100 or percent < 1:
                    raise ValueError("Percent cannot be larger than 100% or under 1%")

                return int(balance / (100 / percent))

            except ValueError:
                raise ValueError("Invalid percent specified.")

        raise ValueError("Invalid amount specified.")

    def generate_data_dir(self, fp: str) -> PrismDataDirectory:
        data_dir = os.path.abspath(os.path.join(os.path.dirname(fp), "data"))
        return PrismDataDirectory(data_dir)

    async def get_message(self, ctx, timeout: int = 5) -> str:
        def check(message):
            return message.author.id == ctx.author.id and message.channel.id == ctx.channel.id

        m = await self.bot.wait_for("message", check = check, timeout = timeout)
        return m.content

    async def wait_for_reaction(self, ctx, message, reactions: list, timeout: int = 10) -> str:
        for r in reactions:
            await message.add_reaction(r)

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message.id == message.id and reaction.emoji in reactions

        m = await self.bot.wait_for("reaction_add", check = check, timeout = timeout)
        return m
