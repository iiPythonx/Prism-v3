# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands
from pyfiglet import Figlet, FigletError

# Command class
class Ascii(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "ascii", "desc": "Turns text into ASCII art.", "cat": "fun", "usage": "ascii <text> [font]"}

        self.fonts = ["starwars", "doom", "goofy", "basic", "block", "chunky", "cricket"]

    @commands.command(pass_context = True)
    async def ascii(self, ctx, text: str = None, font: str = None) -> any:
        if text is None or (text and not text.strip()):
            return await ctx.send(embed = self.core.small_embed("usage: ascii <text> [font]\nTo use spaces, quote your text (eg. \"hello world\")."))

        elif font is None:
            font = self.fonts[0]

        elif font not in self.fonts:
            return await ctx.send(embed = self.core.small_embed(f"Fonts: {self.core.format_list(self.fonts)}"))

        # Construct ASCII art
        try:
            result = Figlet(font = font).renderText(text)
            try:
                return await ctx.send(f"```\n{result}\n```")

            except discord.HTTPException:
                return await ctx.send(embed = self.core.error("Text is too long."))

        except FigletError:
            return await ctx.send(embed = self.core.error("Error parsing text."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Ascii(bot))
