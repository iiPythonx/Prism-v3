# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands
from discord.utils import sane_wait_for

# Command class
class Customize(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "customize", "desc": "Allows you to customize your profile.", "cat": "misc", "usage": "customize <option> <value>"}

        self._valid_keys = ["bio"]

    @commands.command(pass_context = True, aliases = ["customise"])
    async def customize(self, ctx, option: str = None, value: str = None, *, extra = None) -> any:
        if extra is not None:
            return await ctx.send(embed = self.core.error("Too many options were provided."))

        elif option is None:
            embed = self.core.embed(title = "Profile Customization", description = f"You can change an option with {ctx.prefix}{ctx.command} <option> <value>\n\nIf you need to use spaces, quote your sentence.\neg. \"Hello, world!\"")
            embed.add_field(name = "Available options", value = self.core.format_list(self._valid_keys), inline = False)
            return await ctx.send(embed = embed)

        elif value is None:
            return await ctx.send(embed = self.core.error(f"Please specify a value for option '{option}'."))

        elif option not in self._valid_keys:
            return await ctx.send(embed = self.core.error("The specified option is not recognized."))

        # Load database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.send(embed = self.core.noacc(ctx, ctx.author))

        db.update({option: value}, ("userid", ctx.author.id))

        # Finish up
        return await ctx.send(embed = self.core.small_embed("Profile successfully updated."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Customize(bot))
