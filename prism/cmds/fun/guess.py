# Copyright 2021 iiPython

# Modules
import math
import random
import asyncio
from discord.ext import commands

# Command class
class Guess(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self._cooldown_time = (60 * 60) * 5

    @commands.slash_command(description = "Earn coins for guessing the right number.")
    async def guess(self, ctx) -> any:
        if self.bot.cooldowns.on_cooldown("guess", ctx.author):
            return await ctx.respond(embed = self.bot.cooldowns.cooldown_text("guess", ctx.author))

        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author))

        # Initialization
        max_num = random.randint(7, 13)
        number = random.randint(1, max_num)

        bal = db.get(("userid", ctx.author.id), "balance")

        # Calculate gain
        try:
            coins = round(math.ceil(bal / 100) * max(math.log(math.floor(bal / 100)) * 0.5, 0) + 500) * 3

        except ValueError:
            coins = 1500

        # Send embed
        embed = self.core.embed(
            title = "Think you can guess it?",
            description = f"I'm thinking of a number between 1 and {max_num}.\nIf you guess it, I'll give you {self.core.format_coins(coins)} coins. You have 5 seconds.\n\nTo guess, simply type the number in chat.",
            footer = ctx
        )
        msg = await ctx.respond(embed = embed)

        # Wait for number
        try:
            m = await self.core.get_message(ctx)
            try:
                if m is None:
                    self.bot.cooldowns.add_cooldown("guess", ctx.author, self._cooldown_time)
                    return await ctx.respond(embed = self.core.error("That doesn't look like a number."))

                m = int(m)
                if m != number:
                    self.bot.cooldowns.add_cooldown("guess", ctx.author, self._cooldown_time)
                    return await ctx.respond(embed = self.core.error(f"Sorry, I was thinking of `{number}`."))

            except ValueError:
                self.bot.cooldowns.add_cooldown("guess", ctx.author, self._cooldown_time)
                return await ctx.respond(embed = self.core.error("Woops, that isn't a number."))

        except asyncio.exceptions.TimeoutError:
            self.bot.cooldowns.add_cooldown("guess", ctx.author, self._cooldown_time)
            return await ctx.respond(embed = self.core.error("You didn't guess in time!"))

        # Update balance
        db.update({"balance": bal + coins}, ("userid", ctx.author.id))

        # Success embed
        embed = self.core.embed(
            title = "Congratulations!",
            description = f"You got the number right, it was `{number}`.\n`{coins}` coins have been added to your balance.",
            footer = ctx
        )
        await msg.edit(embed = embed)
        return self.bot.cooldowns.add_cooldown("guess", ctx.author, self._cooldown_time)

# Link
def setup(bot) -> None:
    return bot.add_cog(Guess(bot))
