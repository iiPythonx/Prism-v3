# Copyright 2021 iiPython

# Modules
import discord
import requests
import urllib.parse
from typing import Union
from discord.ext import commands
from discord.commands import Option

# Command class
class UrbanDictionary(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

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

    @commands.slash_command(description = "Searches Urban Dictionary for a phrase.", category = "fun")
    @commands.is_nsfw()
    async def dict(self, ctx, phrase: Option(str, "The phrase to lookup")) -> any:
        try:
            data = self.search(phrase)
            if data is None:
                return await ctx.respond(embed = self.core.error("No results found."))

            try:
                return await ctx.respond(embed = self.core.embed(title = data["word"], description = data["definition"], url = data["permalink"], footer = ctx))

            except discord.HTTPException:
                return await ctx.respond(embed = self.core.error("The definition is too long to send."))

        except ConnectionError:
            return await ctx.respond(embed = self.core.error("Failed to connect to Urban Dictionary.\nTry again later."))

# Link
def setup(bot) -> None:
    return bot.add_cog(UrbanDictionary(bot))
