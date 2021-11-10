# Copyright 2021 iiPython

# Modules
import math
from discord.ext import commands

# Command class
class Daily(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self._cooldown = 86400

    @commands.slash_command(description = "Get free coins everyday.", category = "currency")
    async def daily(self, ctx) -> any:
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author))

        elif self.bot.cooldowns.on_cooldown("daily", ctx.author):
            return await ctx.respond(embed = self.bot.cooldowns.cooldown_text("daily", ctx.author))

        bal = db.get(("userid", ctx.author.id), "balance")
        try:
            earn = round(math.ceil(bal / 100) * max(math.log(math.floor(bal / 100)) * 0.2, 0) + 400)

        except ValueError:
            earn = 300

        db.update({"balance": bal + earn}, ("userid", ctx.author.id))
        self.bot.cooldowns.add_cooldown("daily", ctx.author, self._cooldown)

        # Handle embed
        embed = self.core.small_embed(f"You redeemed `{self.core.format_coins(earn)}` coin(s).", footer = ctx)
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Daily(bot))
