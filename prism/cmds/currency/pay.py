# Copyright 2021 iiPython

# Modules
from typing import Union
import discord
from discord.ext import commands

# Command class
class Pay(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "pay", "desc": "Pays another user using coins from your balance.", "cat": "currency", "usage": "pay <user> <amt>"}

    @commands.command(pass_context = True)
    async def pay(self, ctx, user: discord.Member = None, amount: Union[str, int] = None) -> any:
        if user is None:
            return await ctx.send(embed = self.core.error("No user specified to pay."))

        # Check user
        if user == ctx.author:
            return await ctx.send(embed = self.core.error("You cannot pay yourself."))

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", user.id)):
            return await ctx.send(embed = self.core.noacc(ctx, user))

        bal = db.get(("userid", ctx.author.id), "balance")

        # Check amount
        if amount is None:
            return await ctx.send(embed = self.core.error("No amount provided."))

        try:
            # Check for a percent
            if amount.endswith("%"):
                if len(amount) > 4 or len(amount) < 2:
                    return await ctx.send(embed = self.core.error("Invalid percent specified."))

                try:
                    percent = int(amount[:-1])
                    if percent > 100 or percent < 1:
                        return await ctx.send(embed = self.core.error("Percent cannot be larger than 100% or under 1%"))

                    amount = int(bal / (100 / percent))

                except ValueError:
                    return await ctx.send(embed = self.core.error("Invalid percent specified."))

            else:
                amount = int(amount)

        except ValueError:
            return await ctx.send(embed = self.core.error("Invalid amount specified."))

        if amount < 1:
            return await ctx.send(embed = self.core.error("You need to pay at least 1 coin."))

        elif amount > bal:
            return await ctx.send(embed = self.core.error("You don't have that many coins."))

        # Handle transaction
        end_user_bal = db.get(("userid", user.id), "balance")
        end_user_bal += amount
        bal -= amount

        db.update({"balance": bal}, ("userid", ctx.author.id))
        db.update({"balance": end_user_bal}, ("userid", user.id))

        # Handle embed
        embed = self.core.embed(
            title = f"{self.core.emojis['checkmark']} | Transaction complete.",
            description = f"Transferred: {self.core.format_coins(amount)} coin(s) | To: {user.mention}\nNew balance: {bal}",
            footer = ctx
        )
        return await ctx.send(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Pay(bot))
