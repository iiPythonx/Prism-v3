# Copyright 2021 iiPython

# Modules
import random
from discord.ext import commands

# Command class
class NHIE(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "neverhaveiever", "desc": "Gives you a random 'never have i ever' question.", "cat": "fun", "usage": "neverhaveiever"}

        self.responses = [
            "walked a dog", "went to a bar", "made some ascii text",
            "peed in a pool", "worn crocs", "walked a tight-rope",
            "been chased by a dog", "farted in an elevator",
            "used the bathroom in darkness", "pretended to be a burglar",
            "pranked my parents", "kissed a stranger", "dyed my hair the wrong color",
            "tried watching television upside down", "killed a pet by accident",
            "been trapped in an elevator", "driven a car naked",
            "woken someone up by snoring", "given someone a black eye"
        ]

    @commands.command(pass_context = True, aliases = ["nhie"])
    async def neverhaveiever(self, ctx,) -> any:
        return await ctx.send(embed = self.core.small_embed("Never have I ever " + random.choice(self.responses) + "."))

# Link
def setup(bot) -> None:
    return bot.add_cog(NHIE(bot))