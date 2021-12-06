# Copyright 2021-xx iiPython

# Modules
import random
from discord.ext import commands

# Command class
class Beg(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self.people = [
            {"name": "Rick Astley", "quote": lambda: "never gonna " + random.choice(["give you up", "let you down", "run around and desert you"])},
            {"name": "iiPython", "quote": lambda: random.choice(["go get a job", "don't spend it on socks", "linux > windows"])},
            {"name": "Dream", "quote": lambda: "*speedrunning music intensifies*"},
            {"name": "Elon Musk", "quote": lambda: random.choice(["buy a tesla pls", "rocket ship go brrrRRR"])},
            {"name": "Bill Gates", "quote": lambda: "i very rich"},
            {"name": "Donald Trump", "quote": lambda: "IM GONNA BUILD A WALL"},  # Slightly political, but come on it's not that bad
            {"name": "Steve Jobs", "quote": lambda: "have you bought the iPhone 14S Pro Max Lite Premium SE yet?"}
        ]

    @commands.slash_command(description = "Beg the rich for money.")
    async def beg(self, ctx) -> any:
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author))

        elif self.bot.cooldowns.on_cooldown("beg", ctx.author):
            return await ctx.respond(embed = self.bot.cooldowns.cooldown_text("beg", ctx.author))

        bal = db.get(("userid", ctx.author.id), "balance")
        earn = random.randint(84, 213)

        db.update({"balance": bal + earn}, ("userid", ctx.author.id))
        self.bot.cooldowns.add_cooldown("beg", ctx.author, 60)

        # Handle embed
        person = random.choice(self.people)
        embed = self.core.embed(
            title = f"{person['name']} gave you {earn} coins.",
            description = f"\"{person['quote']()}\"",
            footer = ctx
        )
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Beg(bot))
