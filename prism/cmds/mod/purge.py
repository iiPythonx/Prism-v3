# Copyright 2021-xx iiPython

# Modules
import discord
from discord.ext import commands
from discord.commands import Option

# Command class
class Purge(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    @commands.slash_command(description = "Clears the current channel.")
    @commands.has_permissions(manage_messages = True)
    async def purge(self, ctx, amount: Option(int, description = "The amount to clear")) -> any:
        if amount > 100:
            amount = 100

        await ctx.channel.purge(limit = amount)
        return await ctx.respond(embed = self.core.small_embed(f"Successfully cleared {amount} message(s)."), delete_after = 2)

# Link
def setup(bot) -> None:
    return bot.add_cog(Purge(bot))
