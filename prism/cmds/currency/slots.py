# Copyright 2021 iiPython

# Modules
import random
import iipython as ip
from discord.ext import commands

# Command class
class Slots(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "slots", "desc": "Spin some slot machines and earn some coins (or lose some).", "cat": "currency", "usage": "slots <bet>"}

        self._mults = {
            3: ["❌"],
            4: ["7️⃣", "🪙"],
            5: ["🍒"]
        }
        self._items = ip.normalize(*list(self._mults[i] for i in self._mults))

    def pick(self) -> str:
        return random.choice(self._items)

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
        picks = [self.pick() for i in ip.xrange(1, 3)]
        results, earn = "  |  ".join(picks), 0
        for mult in self._mults:
            brk = False
            for emoji in self._mults[mult]:
                if results.count(emoji) == 3:
                    earn = bet * mult
                    brk = True
                    break

            if brk:
                break

        # Save data
        db.update({"balance": bal + (earn or -bet)}, ("userid", ctx.author.id))
        self.bot.cooldowns.add_cooldown("slots", ctx.author, 120)

        # Send embed
        return await ctx.send(embed = self.core.embed(
            title = results,
            description = f"{f'You won `{self.core.format_coins(earn)}`' if earn else f'You lost your `{self.core.format_coins(bet)}`'} coin(s)."
        ))

# Link
def setup(bot) -> None:
    return bot.add_cog(Slots(bot))
