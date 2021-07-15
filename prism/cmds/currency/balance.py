# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands

# Command class
class Balance(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "balance", "desc": "Checks somebodies account balance.", "cat": "currency", "usage": "balance [user]"}

    @commands.command(pass_context = True, aliases = ["bal"])
    async def balance(self, ctx, user: discord.Member = None) -> any:
        if user is None:
            user = ctx.author

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", user.id)):
            return await ctx.send(embed = self.core.noacc(ctx, user))

        bal = db.get(("userid", user.id), "balance")

        # Handle embed
        embed = self.core.small_embed(f"{'You have' if user == ctx.author else f'{user.nick if user.nick is not None else user.name} has'} {bal} coin(s).", footer = ctx)
        embed.set_author(name = "Balance")
        return await ctx.send(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Balance(bot))
