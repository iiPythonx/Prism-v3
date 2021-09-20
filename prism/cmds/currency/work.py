# Copyright 2021 iiPython

# Modules
import math
from discord.ext import commands

# Command class
class Work(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "work", "desc": "Allows you to work for money.", "cat": "currency", "usage": "work"}

    @commands.command(pass_context = True)
    async def work(self, ctx) -> any:

        # Handle cooldowns
        if self.bot.cooldowns.on_cooldown("work", ctx.author):
            return await ctx.send(embed = self.bot.cooldowns.cooldown_text("work", ctx.author))

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.send(embed = self.core.noacc(ctx, ctx.author))

        bal = db.get(("userid", ctx.author.id), "balance")

        # Calculate gain
        try:
            gain = round(math.ceil(bal / 100) * max(math.log(math.floor(bal / 100)) * 0.5, 0) + 500)

        except ValueError:
            gain = 500

        # Save to database
        db.update({"balance": bal + gain}, ("userid", ctx.author.id))

        # Set cooldown
        self.bot.cooldowns.add_cooldown("work", ctx.author, 3600)

        # Send embed
        embed = self.core.embed(title = "Shift complete.", description = f"Coins gained: {gain} coin(s)\nNew balance: {self.core.format_coins(bal + gain)} coin(s)")
        embed.set_thumbnail(url = ctx.author.avatar.url)
        embed.set_footer(text = "| Come back in an hour.", icon_url = ctx.author.avatar.url)
        return await ctx.send(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Work(bot))
