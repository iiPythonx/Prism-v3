# Copyright 2021-xx iiPython

# Modules
import discord
from discord.ext import commands
from discord.commands import Option

# Command class
class Ban(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    @commands.slash_command(description = "Bans a user from the server")
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, user: Option(discord.Member, "The user to ban"), reason: Option(str, "Reason of ban", required = False, default = "None specified.")) -> any:
        try:
            await user.ban(reason = reason)

        except Exception:
            return await ctx.respond(embed = self.core.error("Missing permission to ban that user."))

        return await ctx.respond(embed = self.core.small_embed(f"Successfully banned {user.name}."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Ban(bot))
