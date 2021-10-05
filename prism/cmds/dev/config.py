# Copyright 2021 iiPython

# Modules
import json
from discord.ext import commands

# Command class
class Config(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.hidden = True

        self.bot.config.merge({
            "cooldowns": True
        })

    @commands.command(pass_context = True)
    @commands.is_owner()
    async def config(self, ctx, key: str = None, value: str = None) -> any:
        if key is None:
            return await ctx.send(embed = self.core.error("You need to specify a key to edit."))

        elif key not in self.bot.config.config:
            return await ctx.send(embed = self.core.error(f"Invalid key: `{key}`."))

        # View config
        if value is None:
            value = self.bot.config.get(key)
            return await ctx.send(embed = self.core.embed(
                title = f"`{key}` | {type(value)}",
                description = f"```\n{value}\n```"
            ))

        # Edit config
        try:
            self.bot.config.set(key, json.loads(value))  # JSON automatic type conversion
            return await ctx.message.add_reaction("✅")

        except json.JSONDecodeError:
            return await ctx.send(embed = self.core.error("Invalid value specified; use JSON syntax."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Config(bot))
