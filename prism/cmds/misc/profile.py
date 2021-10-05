# Copyright 2021 iiPython

# Modules
from discord.ext import commands

# Command class
class Profile(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "profile", "desc": "Shows somebodies profile.", "cat": "misc", "usage": "profile [user]"}

    @commands.command(pass_context = True)
    async def profile(self, ctx, user = None) -> any:
        user = self.core.get_user(ctx, user or ctx.author)
        if user is None:
            return await ctx.send(embed = self.core.nouser())

        # Load database
        db = self.bot.db.load_db("users")
        info = db.get(("userid", user.id))
        if info == -1:
            return await ctx.send(embed = self.core.noacc(ctx, user))

        # Construct embed
        embed = self.core.embed(
            title = str(user),
            description = f"\"{info['bio']}\"" if info["bio"] else "",
            footer = ctx,
            color = self.core.color(info["accent"])
        )
        embed.add_field(name = "Balance", value = f"{self.core.format_coins(info['balance'])} coin(s)", inline = False)
        embed.set_thumbnail(url = user.avatar.url)
        return await ctx.send(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Profile(bot))
