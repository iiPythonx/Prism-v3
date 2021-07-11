# Copyright 2021 iiPython

# Modules
from discord.ext import commands

# Command class
class Inventory(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.hidden = True

    @commands.command(pass_context = True)
    async def test_inv(self, ctx) -> any:
        await ctx.send(f"users inventory: {self.bot.objects['inv'](ctx.author.id).items}")
        self.bot.objects["inv"](ctx.author.id).add_item("test item")


# Link
def setup(bot) -> None:
    return bot.add_cog(Inventory(bot))
