# Copyright 2021-xx iiPython

# Modules
import os
import psutil
import discord
from prism import __version__
from discord.ext import commands

# Command class
class Stats(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    def _format_sectors(self, lines: list) -> str:
        return "".join("> " + line + "\n" for line in lines)[:-1]

    @commands.slash_command(description = "Show Prism's system information.")
    async def stats(self, ctx) -> any:

        # Initialization
        vm = psutil.virtual_memory()
        mem_av = self.core.scale_size(vm.used, add_suffix = False)
        mem_tl = self.core.scale_size(vm.total)

        # Construct embed
        embed = self.core.embed(title = "System Statistics", footer = ctx)
        embed.add_field(
            name = "Bot info",
            value = self._format_sectors([
                f"Account: {self.bot.user}",
                f"Server count: {len(self.bot.guilds)} server(s)",
                f"Bot version - v{__version__}",
                f"Libary version: {discord.__version__}"
            ]),
            inline = False
        )
        embed.add_field(
            name = "System info",
            value = self._format_sectors([
                f"PID: {os.getpid()}",
                f"Memory usage: {mem_av}/{mem_tl}",
                f"Git version: {self.core.fetch_output('git --version', split = (' ', 2))}",
                f"Host: {self.core.fetch_output('uname -s -r -o')}"
            ]),
            inline = False
        )
        embed.set_thumbnail(url = self.bot.user.avatar.url)
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Stats(bot))
