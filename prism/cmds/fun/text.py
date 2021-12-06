# Copyright 2021-xx iiPython

# Modules
import random
import discord
from discord.ext import commands
from discord.commands import Option

# Command class
class Text(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self.actions = {
            "scramble": self.scramble,
            "caps": self.caps
        }

    def scramble(self, text: str) -> str:
        chars = list(text)
        random.shuffle(chars)
        return "".join(chars)

    def caps(self, text: str) -> str:
        return "".join([getattr(char, random.choice(["lower", "upper"]))() for char in list(text)])

    @commands.slash_command(description = "Mess around with text in weird ways.")
    async def text(self, ctx, action: Option(str, "The action to perform", choices = ["scramble", "caps"]), text: Option(str, "The text to mess with")) -> any:
        try:
            return await ctx.respond(self.actions[action](text))

        except discord.HTTPException:
            return await ctx.respond(embed = self.core.error("Your text is too long."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Text(bot))
