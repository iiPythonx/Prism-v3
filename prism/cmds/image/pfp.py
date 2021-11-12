# Copyright 2021 iiPython

# Modules
import discord
from discord.ext import commands
from discord.commands import Option

# Command class
class Avatar(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

    @commands.slash_command(description = "Shows you somebodies profile picture.", category = "image")
    async def avatar(self, ctx, user: Option(discord.Member, "The user with the profile picture", reuqired = False)) -> any:
        user = user or ctx.author

        # Construct embed
        embed = self.core.embed(
            title = str(user),
            description = f"[[Raw Image]({user.avatar.url})] [[{user.name}'s Profile](https://discord.com/users/{user.id})]",
            footer = ctx
        )
        embed.set_image(url = user.avatar.url)
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Avatar(bot))
