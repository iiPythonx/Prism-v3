# Copyright 2021 iiPython

# Modules
import random
from discord.ext import commands

# Command class
class Slots(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "slots", "desc": "Spin some slot machines and earn some coins (or lose some).", "cat": "currency", "usage": "slots <bet>"}

    def pick(self) -> str:
        return random.choice([":coin:", ":cherries:"])

    @commands.command(pass_context = True)
    async def slots(self, ctx, bet: int = None) -> any:
        if bet is None:
            return await ctx.send(embed = self.core.error("You need to specify a bet."))

        elif self.bot.cooldowns.on_cooldown("slots", ctx.author):
            return await ctx.send(embed = self.bot.cooldowns.cooldown_text("slots", ctx.author))

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.send(embed = self.core.noacc(ctx, ctx.author))

        bal = db.get(("userid", ctx.author.id), "balance")
        if bet < 100:
            return await ctx.send(embed = self.core.error("You need to bet at least 100 coins."))

        elif bet > bal:
            return await ctx.send(embed = self.core.error("You don't have that many coins."))

        # Handle results
        results, earn = f"{self.pick()}\t{self.pick()}\t{self.pick()}", 0
        if results.count("coin") == 3:
            earn = bet * 3

        elif results.count("cherries") == 3:
            earn = bet * 5

        # Save data
        db.update({"balance": bal + (earn or -bet)}, ("userid", ctx.author.id))
        self.bot.cooldowns.add_cooldown("slots", ctx.author, 120)

        # Send embed
        return await ctx.send(embed = self.core.embed(
            title = f"▶️\t{results}",
            description = f"{f'You won `{self.core.format_coins(earn)}`' if earn else f'You lost your `{self.core.format_coins(bet)}`'} coin(s)."
        ))

# Link
def setup(bot) -> None:
    return bot.add_cog(Slots(bot))
