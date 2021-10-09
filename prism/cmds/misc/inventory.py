# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands

# Command class
class Inventory(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "inventory", "desc": "Displays a users inventory.", "cat": "misc", "usage": "inventory [user]"}

    @commands.command(pass_context = True, aliases = ["inv"])
    async def inventory(self, ctx, user: discord.User = None) -> any:
        if user is None:
            user = ctx.author

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", user.id)):
            return await ctx.send(embed = self.core.noacc(ctx, user))

        user_inv = self.core.inventory(user.id).items

        # Construct embed
        embed = self.core.embed(
            title = f"""{f"{user.name}'s " if user != ctx.author else "Your "}Inventory""",
            description = self.core.format_list([f"{item}{f' (x{user_inv[item]})' if user_inv[item] > 1 else ''}" for item in user_inv]) if user_inv else "Nothing to display.",
            footer = ctx
        )
        embed.set_thumbnail(url = user.avatar.url)
        return await ctx.send(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Inventory(bot))
