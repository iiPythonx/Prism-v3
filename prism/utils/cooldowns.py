# Copyright 2021 iiPython

# Modules
import discord
import itertools
from typing import Union
from discord.ext import commands
from datetime import datetime, timedelta

# Cooldowns object
class Cooldowns(object):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cooldowns = {}

    def _grab_time(self, time: int) -> datetime:
        return datetime.now() + timedelta(seconds = time)

    def _format_time(self, seconds: int) -> str:
        utc_time = datetime.utcfromtimestamp(seconds)
        values = timedelta(seconds = seconds).days, utc_time.hour, utc_time.minute, utc_time.second
        non_zero = tuple(itertools.dropwhile(lambda x: not x[0], zip(values, "dhms")))
        format_str = "{:0>2}{} {:0>2}{}" if len(non_zero) > 1 else " {:0>2}s"
        return format_str.format(*itertools.chain.from_iterable(non_zero or ((0, 0),)))

    def add_cooldown(self, name: str, user: Union[discord.User, discord.Member], time: int) -> None:
        if not hasattr(user, "id"):
            raise RuntimeError("provided cooldown user has no id attribute.")

        # Handle initialization
        if user.id not in self.cooldowns:
            self.cooldowns[user.id] = {name: self._grab_time(time)}

        else:

            # Create cooldown
            self.cooldowns[user.id][name] = self._grab_time(time)

    def on_cooldown(self, name: str, user: Union[discord.User, discord.Member]) -> bool:
        if self.bot.config.get("cooldowns") is False:
            return False

        if not hasattr(user, "id"):
            raise RuntimeError("provided cooldown user has no id attribute.")

        elif user.id not in self.cooldowns:
            return False

        elif name not in self.cooldowns[user.id]:
            return False

        # Check time
        remaining = round((self.cooldowns[user.id][name] - datetime.now()).total_seconds())
        if remaining <= 0:
            del self.cooldowns[user.id][name]
            if not self.cooldowns[user.id]:
                del self.cooldowns[user.id]

            return False

        return True

    def cooldown_text(self, name: str, user: Union[discord.User, discord.Member]) -> discord.Embed:
        if not hasattr(user, "id"):
            raise RuntimeError("provided cooldown user has no id attribute.")

        elif user.id not in self.cooldowns:
            raise RuntimeError("given user has no cooldowns.")

        elif name not in self.cooldowns[user.id]:
            raise RuntimeError("given user has no cooldown under name '{}'".format(name))

        # Construct embed
        remaining = self._format_time(round((self.cooldowns[user.id][name] - datetime.now()).total_seconds()))
        return self.bot.core.error(f"You are on cooldown. {remaining} remaining.")
