# Copyright 2021 iiPython

# Modules
from discord.ext import commands

# Command class
class Create(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    @commands.slash_command(description = "Creates a Prism account.", category = "currency")
    async def create(self, ctx) -> any:
        db = self.bot.db.load_db("users")
        if db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.error("You already have a Prism account."))

        db.create((ctx.author.id, 100, "", self.core.storage["accent"]))
        return await ctx.respond(embed = self.core.small_embed(":tada: You now have a Prism account."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Create(bot))
