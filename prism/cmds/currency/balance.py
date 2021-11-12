# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands
from discord.commands import Option

# Command class
class Balance(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    @commands.slash_command(description = "Checks somebodies account balance.", category = "currency")
    async def balance(self, ctx, user: Option(discord.Member, "The user to check the balance of", required = False) = None) -> any:
        user = user or ctx.author

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", user.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, user))

        bal = db.get(("userid", user.id), "balance")

        # Handle embed
        embed = self.core.small_embed(f"{'You have' if user == ctx.author else f'{user.nick if user.nick is not None else user.name} has'} {self.core.format_coins(bal)} coin(s).", footer = ctx)
        embed.set_author(name = "Balance")
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Balance(bot))
