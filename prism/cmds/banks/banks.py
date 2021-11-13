# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands
from discord.commands import Option
from prism.core.banks import (
    get_bank_balance, can_deposit, bank_deposit,
    bank_withdraw, _bank_max_val
)

# Command class
class Banks(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    @commands.slash_command(description = "Shows your bank status", category = "currency")
    async def bank(self, ctx, user: Option(discord.Member, "The user to view the bank of", required = False) = None) -> any:
        user = user or ctx.author

        # Check for account
        if not self.bot.db.load_db("users").test_for(("userid", user.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, user))

        bank_bal = get_bank_balance(user.id)

        # Handle embed
        embed = self.core.embed(title = f"{self.core.frmt_name(ctx.author)}'s Bank", footer = ctx)
        embed.add_field(
            name = "Bank usage",
            value = f"{self.core.format_coins(bank_bal)}/{self.core.format_coins(_bank_max_val)} coin(s) ({round(bank_bal / _bank_max_val, 2)}%)"
        )
        embed.set_thumbnail(url = user.avatar.url)
        return await ctx.respond(embed = embed)

    @commands.slash_command(description = "Deposits coins into your bank", category = "currency")
    async def deposit(self, ctx, amount: Option(str, "The amount to deposit")) -> any:
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author.id))

        # Handle amount conversion
        user_bal = db.get(("userid", ctx.author.id), "balance")
        try:
            amount = int(amount)

        except ValueError:
            try:
                amount = self.core.amountstr_to_bal(amount, user_bal)

            except ValueError as e:
                return await ctx.respond(embed = self.core.error(str(e)))

        # Amount checks
        if amount < 1:
            return await ctx.respond(embed = self.core.error("You need to deposit at least 1 coin."))

        elif amount > user_bal:
            return await ctx.respond(embed = self.core.error("You don't have that many coins."))

        elif not can_deposit(ctx.author.id, amount):
            return await ctx.respond(embed = self.core.error("You cannot deposit that many coins."))

        # Handle deposit
        bank_deposit(ctx.author.id, amount, db)
        return await ctx.respond(embed = self.core.small_embed("Successfully deposited."))

    @commands.slash_command(description = "Withdraws coins from your bank", category = "currency")
    async def withdraw(self, ctx, amount: Option(str, "The amount to withdraw")) -> any:
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author.id))

        # Handle amount conversion
        bank_bal = get_bank_balance(ctx.author.id)
        try:
            amount = int(amount)

        except ValueError:
            try:
                amount = self.core.amountstr_to_bal(amount, bank_bal)

            except ValueError as e:
                return await ctx.respond(embed = self.core.error(str(e)))

        # Amount checks
        if amount < 1:
            return await ctx.respond(embed = self.core.error("You need to withdraw at least 1 coin."))

        elif amount > bank_bal:
            return await ctx.respond(embed = self.core.error("You don't have that many coins in your bank."))

        # Handle deposit
        bank_withdraw(ctx.author.id, amount, db)
        return await ctx.respond(embed = self.core.small_embed("Successfully withdrew."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Banks(bot))
