# Copyright 2021 iiPython

# Modules
import random
import asyncio
from discord.ext import commands

# Command class
class RPS(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "rps", "desc": "Play Rock Paper Scissors.", "cat": "fun", "usage": "rps"}

        self._resp = ["🪨", "📰", "✂️"]
        self._resdict = {-1: "You won!", 0: "Tie!", 1: "I won!"}

    def pick(self) -> str:
        return random.choice(self._resp)

    def rate(self, first: str, second: str) -> int:
        if first == second:
            return 0

        elif first == "🪨" and second == "✂️":
            return -1

        elif first == "📰" and second == "🪨":
            return -1

        elif first == "✂️" and second == "📰":
            return -1

        else:
            return 1

    @commands.command(pass_context = True)
    async def rps(self, ctx) -> any:
        results = []
        for i in range(3):
            em = self.core.embed(title = f"Round {i + 1}")
            try:
                msg = await ctx.send(embed = em)
                reaction = await self.core.wait_for_reaction(ctx, msg, self._resp)

            except asyncio.exceptions.TimeoutError:
                return await ctx.send(embed = self.core.error("You didn't respond in time."))

            ans = self.pick()
            reaction = reaction[0].emoji
            results.append(self.rate(reaction, ans))

            em.title += f" - {self._resdict[results[-1]]}"
            em.description = f"Me: {ans} | You: {reaction}"
            await msg.edit(embed = em)

        # Final embed
        title = ("You won!" if results.count(-1) > results.count(1) else "") or ("I won!" if results.count(1) > results.count(-1) else "") or "Tie!"
        embed = self.core.embed(
            title = title,
            description = f"I got {results.count(1)}/3; you got {results.count(-1)}/3.",
            footer = ctx
        )

        return await ctx.send(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(RPS(bot))
