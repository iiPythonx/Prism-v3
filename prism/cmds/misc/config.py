# Copyright 2021 iiPython

# Modules
from typing import Any
from discord.ext import commands

# Command class
class Config(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "config", "desc": "Change the bots settings for your server.", "cat": "misc", "usage": "config <option> <value>"}

        self._valid_keys = {}
        if self.bot.config.get(["prefix", "allow_change"]):
            self._valid_keys["prefix"] = self._check_prefix

    def _check_prefix(self, prefix: str) -> Any:
        if len(prefix) > 20:
            return self.core.error("Maximum prefix length is 20 characters.")

        elif not prefix.strip():
            return self.core.error("Prefix is missing.")

        return None

    @commands.command(pass_context = True)
    @commands.has_guild_permissions(manage_guild = True, administrator = True, manage_roles = True)
    async def config(self, ctx, key: str = None, value: str = None) -> any:
        if key is None:
            embed = self.core.embed(title = "Server Configuration", description = f"You can change an option with `{ctx.prefix}{ctx.command} <option> <value>`\n\nIf you need to use spaces, quote your sentence.\neg. `{ctx.prefix}{ctx.command} prefix \"cheese pizza: \"`")
            embed.add_field(name = "Available options", value = self.core.format_list(self._valid_keys), inline = False)
            return await ctx.send(embed = embed)

        elif key not in self._valid_keys:
            return await ctx.send(embed = self.core.error("Invalid key specified."))

        elif value is None or (value and not value.strip()):
            return await ctx.send(embed = self.core.error("No value specified."))

        elif len(value) > 25:
            return await ctx.send(embed = self.core.error("Max value size is 25 characters."))

        # Load database
        guilds = self.bot.db.load_db("guilds")
        if not guilds.test_for(("id", ctx.guild.id)):
            guilds.create((ctx.guild.id, self.bot.config.get(["prefix", "value"])))

        # Handle check
        error = self._valid_keys[key](value)
        if error is not None:
            return await ctx.send(embed = error)

        guilds.update({key: value}, ("id", ctx.guild.id))
        return await ctx.send(embed = self.core.small_embed("Configuration updated."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Config(bot))
