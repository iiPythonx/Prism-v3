# Copyright 2021-xx iiPython

# Modules
import discord
from discord.ext import commands
from discord.commands import Option

# Command class
class Pay(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    @commands.slash_command(description = "Pays another user using coins from your balance.")
    async def pay(self, ctx, user: Option(discord.Member, "The user you wish to pay."), amount: Option(str, "The amount to pay.")) -> any:
        if user == ctx.author:
            return await ctx.respond(embed = self.core.error("You cannot pay yourself."))

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", user.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, user))

        bal = db.get(("userid", ctx.author.id), "balance")

        # Check amount
        try:
            amount = int(amount)

        except ValueError:
            try:
                amount = self.core.amountstr_to_bal(amount, bal)

            except ValueError:
                return await ctx.respond(embed = self.core.error("Invalid amount specified."))

        if amount < 1:
            return await ctx.respond(embed = self.core.error("You need to pay at least 1 coin."))

        elif amount > bal:
            return await ctx.respond(embed = self.core.error("You don't have that many coins."))

        # Handle transaction
        end_user_bal = db.get(("userid", user.id), "balance")
        end_user_bal += amount
        bal -= amount

        db.update({"balance": bal}, ("userid", ctx.author.id))
        db.update({"balance": end_user_bal}, ("userid", user.id))

        # Handle embed
        embed = self.core.embed(
            title = f"{self.core.emojis['checkmark']} | Transaction complete.",
            description = f"Transferred: {self.core.format_coins(amount)} coin(s) | To: {user.mention}\nNew balance: {self.core.format_coins(bal)}",
            footer = ctx
        )
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Pay(bot))
