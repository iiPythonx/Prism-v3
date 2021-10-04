# Copyright 2021 iiPython

# Modules
from discord.ext import commands

# Command class
class Avatar(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "avatar", "desc": "Shows you somebodies profile picture.", "cat": "image", "usage": "avatar [user]"}

    @commands.command(pass_context = True, aliases = ["pfp", "av"])
    async def avatar(self, ctx, user = None) -> any:
        user = self.core.get_user(ctx, user or ctx.author)
        if user is None:
            return await ctx.send(embed = self.core.nouser())

        # Construct embed
        embed = self.core.embed(
            title = str(user),
            description = f"[[Raw Image]({user.avatar.url})] [[{user.name}'s Profile](https://discord.com/users/{user.id})]",
            footer = ctx
        )
        embed.set_image(url = user.avatar.url)
        return await ctx.send(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Avatar(bot))
