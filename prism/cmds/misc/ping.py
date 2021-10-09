# Copyright 2021 iiPython

# Modules
from discord.ext import commands

# Command class
class Ping(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "ping", "desc": "Displays the bots ping time.", "cat": "misc", "usage": "ping"}

    @commands.command(pass_context = True)
    async def ping(self, ctx) -> any:

        # Test API ping
        tid = self.core.timer.start()
        message = await ctx.send(embed = self.core.embed(description = "**Checking ping...**"))
        api_ping = self.core.timer.end(tid, return_as = "ms", as_int = True)

        # Test bot ping
        bot_ping = round(self.bot.latency * 1000)

        # Show ping
        embed = self.core.embed(title = "Pong :ping_pong:", description = f"Bot: {bot_ping}ms | API: {api_ping}ms\nRoundtrip: {api_ping + bot_ping}ms")
        return await message.edit(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Ping(bot))
