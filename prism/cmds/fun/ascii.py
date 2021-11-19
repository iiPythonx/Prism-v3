# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands
from discord.commands import Option
from pyfiglet import Figlet, FigletError

# Command class
class Ascii(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    @commands.slash_command(description = "Turns text into ASCII art.")
    async def ascii(
        self,
        ctx,
        text: Option(str, "The text to ASCIIify"),
        font: Option(
            str,
            "The font to use",
            choices = ["starwars", "doom", "goofy", "basic", "block", "chunky", "cricket"],  # noqa
            required = False,
            default = "starwars"  # noqa
        )
    ) -> any:
        try:
            result = Figlet(font = font).renderText(text)
            try:
                return await ctx.respond(f"```\n{result}\n```")

            except discord.HTTPException:
                return await ctx.respond(embed = self.core.error("Text is too long."))

        except FigletError:
            return await ctx.respond(embed = self.core.error("Error parsing text."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Ascii(bot))
