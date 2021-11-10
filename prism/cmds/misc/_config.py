# Copyright 2021 iiPython
# NOT IN USE: slash commands remove the need for a changable prefix

# Modules
from typing import Any
from discord.ext import commands
from discord.commands import Option

# Command class
class Config(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self._valid_keys = {}
        if self.bot.config.get(["prefix", "allow_change"]):
            self._valid_keys["prefix"] = self._check_prefix

    def _check_prefix(self, prefix: str) -> Any:
        if len(prefix) > 20:
            return self.core.error("Maximum prefix length is 20 characters.")

        elif not prefix.strip():
            return self.core.error("Prefix is missing.")

        return None

    @commands.slash_command(description = "Change Prism's settings for your server.", category = "misc")
    @commands.has_guild_permissions(manage_guild = True)
    async def config(self, ctx, key: Option(str, "The option you wish to change", choices = ["prefix"]), value: Option(str, "The new value")) -> any:  # noqa
        if key not in self._valid_keys:
            return await ctx.respond(embed = self.core.error("Invalid key specified."))

        elif len(value) > 25:
            return await ctx.respond(embed = self.core.error("Max value size is 25 characters."))

        # Load database
        guilds = self.bot.db.load_db("guilds")
        if not guilds.test_for(("id", ctx.guild.id)):
            guilds.create((ctx.guild.id, self.bot.config.get(["prefix", "value"])))

        # Handle check
        error = self._valid_keys[key](value)
        if error is not None:
            return await ctx.respond(embed = error)

        guilds.update({key: value}, ("id", ctx.guild.id))
        return await ctx.respond(embed = self.core.small_embed("Configuration updated."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Config(bot))
