# Copyright 2021 iiPython

# Modules
from prism import __version__
from discord.ext import commands

# Command class
class Version(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "version", "desc": "Provides the current version information.", "cat": "misc", "usage": "version [branch]"}

    @commands.command(pass_context = True, aliases = ["ver"])
    async def version(self, ctx) -> any:

        # Grab git information
        last_commit = self.core.fetch_output("git log -1 --pretty=format:%B")
        last_author = self.core.fetch_output(["git", "log", "-1", "--pretty=format:'%an <%ae>'"]).strip("'")
        curr_branch = self.core.fetch_output("git branch --show-current")
        last_modify = self.core.fetch_output("git log -1 --pretty=format:%cd")

        # Construct embed
        embed = self.core.embed(
            title = f"Prism v{__version__} - Build Info",
            description = f"Current branch: `{curr_branch}`",
            footer = ctx
        )
        embed.add_field(name = "Last commit", value = f"```\n\"{last_commit}\" (by {last_author})\n```", inline = False)
        embed.add_field(name = "Last modified", value = f"```\n{last_modify}\n```", inline = False)
        return await ctx.send(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Version(bot))
