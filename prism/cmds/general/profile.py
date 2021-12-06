# Copyright 2021-xx iiPython

# Modules
import discord
from discord.ext import commands
from discord.commands import Option

# Command class
class Profile(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    @commands.slash_command(description = "View somebodies profile.")
    async def profile(self, ctx, user: Option(discord.Member, "The user to view", required = False) = None) -> any:
        user = user or ctx.author

        # Load database
        db = self.bot.db.load_db("users")
        info = db.get(("userid", user.id))
        if info is None:
            return await ctx.respond(embed = self.core.noacc(ctx, user))

        # Construct embed
        embed = self.core.embed(
            title = str(user),
            description = f"\"{info['bio']}\"" if info["bio"] else "",
            footer = ctx,
            color = self.core.color(info["accent"])
        )
        embed.add_field(name = "Balance", value = f"{self.core.format_coins(info['balance'])} coin(s)", inline = False)
        embed.set_thumbnail(url = user.avatar.url)
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Profile(bot))
