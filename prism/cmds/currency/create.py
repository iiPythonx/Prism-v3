# Copyright 2021 iiPython

# Modules
from discord.ext import commands

# Command class
class Create(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "create", "desc": "Creates a Prism account.", "cat": "currency", "usage": "create"}

    @commands.command(pass_context = True)
    async def create(self, ctx) -> any:
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.send(embed = self.core.error("You already have a Prism account."))

        db.create((ctx.author.id, 100))
        return await ctx.send(embed = self.core.embed("You now have a Prism account."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Create(bot))
