# Copyright 2021-xx iiPython

# Modules
import discord
from discord.ext import commands

# Command class
class Invite(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    @commands.slash_command(description = "Invite Prism to your server.")
    async def invite(self, ctx) -> any:
        if not hasattr(self, "url"):
            self.url = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=2147609664&scope=applications.commands%20bot"

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label = "Invite", url = self.url, style = discord.ButtonStyle.url))
        return await ctx.respond(embed = self.core.small_embed("Invite Prism to your server."), view = view)

# Link
def setup(bot) -> None:
    return bot.add_cog(Invite(bot))
