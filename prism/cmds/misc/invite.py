# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands

# Button handler
class InviteButton(discord.ui.View):
    def __init__(self, url: str) -> None:
        super().__init__()
        self.invite.url = url

    @discord.ui.button(label = "Invite", url = "")
    async def invite(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        return

# Command class
class Invite(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "invite", "desc": "Allows you to invite the bot.", "cat": "misc", "usage": "invite"}

        self.perms = 2147609664

    @commands.command(pass_context = True)
    async def invite(self, ctx) -> any:
        url = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions={self.perms}&scope=bot"
        return await ctx.send(embed = self.core.small_embed("Invite Prism to your server."), view = InviteButton(url))

# Link
def setup(bot) -> None:
    return bot.add_cog(Invite(bot))
