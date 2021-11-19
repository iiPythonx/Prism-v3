# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands
from discord.commands import Option

# Command class
class Kick(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    @commands.slash_command(description = "Kicks a user from the server")
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, user: Option(discord.Member, "The user to kick"), reason: Option(str, "Reason of kick", required = False, default = "None specified.")) -> any:
        try:
            await user.kick(reason = reason)

        except Exception:
            return await ctx.respond(embed = self.core.error("Missing permission to kick that user."))

        return await ctx.respond(embed = self.core.small_embed(f"Successfully kicked {user.name}."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Kick(bot))
