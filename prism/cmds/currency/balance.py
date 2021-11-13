# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands
from discord.commands import Option
from prism.core.banks import get_bank_balance

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
        bank_bal = get_bank_balance(user.id)

        # Handle embed
        embed = self.core.embed(title = str(user), footer = ctx)
        embed.add_field(name = "Balance", value = f"{self.core.format_coins(bal)} coin(s)", inline = False)
        embed.add_field(name = "Bank Balance", value = f"{self.core.format_coins(bank_bal)} coin(s)", inline = False)
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Balance(bot))
