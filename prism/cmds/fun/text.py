# Copyright 2021 iiPython

# Modules
import random
import discord
from discord.ext import commands

# Command class
class Text(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "text", "desc": "Lets you mess around with text.", "cat": "fun", "usage": "text <action> <text>"}

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

    @commands.command(pass_context = True)
    async def text(self, ctx, action: str = None, *, text: str = None) -> any:
        if action is None:
            return await ctx.send(embed = self.core.error(f"No action specified, run `{ctx.prefix}text actions` to get a list."))

        elif action == "actions":
            return await ctx.send(embed = self.core.small_embed("Actions available:\n" + self.core.format_list(self.actions)))

        elif action not in self.actions:
            return await ctx.send(embed = self.core.error(f"Unknown action; run `{ctx.prefix}text actions` to get a list."))

        elif text is None or (text and not text.strip()):
            return await ctx.send(embed = self.core.error("No text specified."))

        # Try and format text
        try:
            return await ctx.send(self.actions[action](text))

        except discord.HTTPException:
            return await ctx.send(embed = self.core.error("Your text is too long."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Text(bot))
