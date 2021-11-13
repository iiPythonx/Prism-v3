# Copyright 2021 iiPython

# Modules
import os
import random
import discord
from PIL import Image as Image_
from discord.ext import commands
from discord.commands import Option

# Praw import
try:
    import praw

except ImportError:
    pass

# Command class
class Image(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        # Connect to reddit
        self._user = None
        try:
            self.reddit = praw.Reddit(
                client_id = os.getenv("REDDIT_CLIENT_ID"),
                client_secret = os.getenv("REDDIT_CLIENT_SEC"),
                password = os.getenv("REDDIT_PASSWORD"),
                username = os.getenv("REDDIT_USERNAME"),
                user_agent = "Prism v3 (by /u/iiPython)"
            )

            self._user = self.reddit.user.me()
            self._sub = self.reddit.subreddit("memes")

        except Exception:
            pass

    def fetch_submission(self, allow_nsfw: bool) -> praw.models.Submission:
        submission = None
        while submission is None:
            _sub = self._sub.random()
            if (not (_sub.over_18 and not allow_nsfw)) and _sub.url.split("//")[0] == "i":
                submission = _sub

            submission = _sub

        return submission

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

    @commands.slash_command(description = "Fetches a random meme from reddit.", category = "image")
    async def meme(self, ctx) -> any:
        if self._user is None:
            return await ctx.respond(embed = self.core.error("This command is currently disabled."))

        # Construct embed
        submission = self.fetch_submission(ctx.channel.is_nsfw())
        embed = self.core.embed(
            title = submission.title,
            url = f"https://reddit.com{submission.permalink}"
        )
        embed.set_image(url = submission.url)
        embed.set_footer(text = u"\N{thumbs up sign}\t{}".format(submission.score))
        return await ctx.respond(embed = embed)

    @commands.slash_command(description = "Is it just me, or are they triggered?", category = "image")
    async def triggered(self, ctx, user: Option(discord.Member, "The user to make triggered", required = False)) -> any:
        user = user or ctx.author

        # Initialization
        image = self.core.images.imagefromURL(user.avatar.url).resize((216, 216), Image.ANTIALIAS)
        text = Image.open(os.path.join(self.core.asset_dir, "img/triggered.jpg"))

        # Animating
        canvas = Image.new(mode = "RGB", size = image.size, color = (0, 0, 0))
        images, num = [], 0
        while num < 100:
            canvas.paste(image, (random.randint(-4, 4), random.randint(-4, 4)))
            images.append(canvas)
            canvas.paste(text, (random.randint(-4, 4), (216 - 39) + (random.randint(-4, 4))))
            canvas = Image.new(mode = "RGB", size = image.size, color = (0, 0, 0))
            num += 5

        # Compiling to GIF
        data = self.core.images.compileGIF(images, 3)

        # Send the image
        return await ctx.respond(file = discord.File(data, "triggered.gif"))

# Link
def setup(bot) -> None:
    return bot.add_cog(Image(bot))
