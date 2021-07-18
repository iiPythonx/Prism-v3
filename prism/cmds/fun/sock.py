# Copyright 2021 iiPython

# Modules
import random
import discord
from discord.ext import commands

# Command class
class Sock(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "sock", "desc": "Socks somebody for some quick cash.", "cat": "fun", "usage": "sock <user>"}

        self._sock_percents = (3, 7)  # 3-7% of their balance
        self._success_msgs = ["rekt", "#pwned", "Imagine getting socked", "Impressive", "GG"]

    @commands.command(pass_context = True)
    async def sock(self, ctx, *, user: discord.Member = None) -> any:
        if user is None:
            return await ctx.send(embed = self.core.error("Tell me who you want to sock."))

        elif user == ctx.author:
            return await ctx.send(embed = self.core.error("Why would you want to sock yourself?"))

        # Handle cooldowns
        if self.bot.cooldowns.on_cooldown("sock", ctx.author):
            return await ctx.send(embed = self.bot.cooldowns.cooldown_text("sock", ctx.author))

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", user.id)):
            return await ctx.send(embed = self.core.noacc(ctx, user))

        elif not db.test_for(("userid", ctx.author.id)):
            return await ctx.send(embed = self.core.noacc(ctx, ctx.author))

        # Handle logic
        if random.randint(1, 10) in range(8):
            obal = db.get(("userid", user.id), "balance")
            lbal = db.get(("userid", ctx.author.id), "balance")

            # Grab percentage
            percent = random.randint(self._sock_percents[0], self._sock_percents[1])
            amount = round(obal / (100 / percent))

            # Update balances
            db.update({"balance": obal - amount}, ("userid", user.id))
            db.update({"balance": lbal + amount}, ("userid", ctx.author.id))

            # Give our nice embed
            uname, oname = self.core.frmt_name(ctx.author), self.core.frmt_name(user)
            await ctx.send(embed = self.core.embed(title = random.choice(self._success_msgs), description = f"{uname} socked {oname} and got away with {self.core.format_coins(amount)} coins."))

        else:
            await ctx.send(embed = self.core.error("Nice try kiddo. You missed your shot."))

        return self.bot.cooldowns.add_cooldown("sock", ctx.author, 300)

# Link
def setup(bot) -> None:
    return bot.add_cog(Sock(bot))
