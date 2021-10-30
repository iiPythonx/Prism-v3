# Copyright 2021 iiPython

# Modules
import discord
import requests
import urllib.parse
from typing import Union
from discord.ext import commands

# Command class
class UrbanDictionary(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "dict", "desc": "Searches Urban Dictionary for a phrase.", "cat": "fun", "usage": "dict <phrase>"}

        self.url = "https://api.urbandictionary.com/v0/define?term={}"

    def search(self, phrase: str) -> Union[dict, None]:
        try:
            req = requests.get(
                self.url.format(urllib.parse.quote(phrase.lower())),
                headers = {"Content-Type": "application/json"},
                timeout = 2
            ).json()
            if not req["list"]:
                return None

            return max(req["list"], key = lambda d: d["thumbs_up"])

        except Exception:
            raise ConnectionError

    @commands.command(pass_context = True, aliases = ["urban", "ud"])
    @commands.is_nsfw()
    async def dict(self, ctx, *, phrase: str = None) -> any:
        if phrase is None or (phrase and not phrase.strip()):
            return await ctx.send(embed = self.core.error("No phrase specified."))

        try:
            data = self.search(phrase)
            if data is None:
                return await ctx.send(embed = self.core.error("No results found."))

            try:
                return await ctx.send(embed = self.core.embed(title = data["word"], description = data["definition"], url = data["permalink"], footer = ctx))

            except discord.HTTPException:
                return await ctx.send(embed = self.core.error("The definition is too long to send."))

        except ConnectionError:
            return await ctx.send(embed = self.core.error("Failed to connect to Urban Dictionary.\nTry again later."))

# Link
def setup(bot) -> None:
    return bot.add_cog(UrbanDictionary(bot))
