# Copyright 2021 iiPython

# Modules
from discord.ext import commands
from discord.commands import Option

# Command class
class Customize(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self._key_checks = {"accent": lambda v: self.core.color(v)}

    @commands.slash_command(description = "Customize your profile.", category = "misc")
    async def customize(self, ctx, option: Option(str, "The option you wish to change", choices = ["bio", "accent"]), value: Option(str, "The new value")) -> any:  # noqa
        try:
            if option in self._key_checks:
                self._key_checks[option](value)

        except Exception:
            return await ctx.respond(embed = self.core.error(f"Invalid value provided for `{option}`."))

        # Load database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.send(embed = self.core.noacc(ctx, ctx.author))

        db.update({option: value}, ("userid", ctx.author.id))

        # Finish up
        return await ctx.respond(embed = self.core.small_embed("Profile successfully updated."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Customize(bot))
