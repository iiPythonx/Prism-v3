# Copyright 2021-xx iiPython

# Modules
import os
from discord.ext import commands

# Praw import
try:
    import praw

except ImportError:
    pass

# Command class
class Meme(commands.Cog):
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

    @commands.slash_command(description = "Fetches a random meme from reddit.")
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

# Link
def setup(bot) -> None:
    return bot.add_cog(Meme(bot))
