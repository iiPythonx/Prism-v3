# Copyright 2021 iiPython

# Modules
from prism import __version__
from discord.ext import commands

# Command class
class Version(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.github_repo = "https://github.com/ii-Python/Prism-v3"

    @commands.slash_command(description = "Show Prism's version.")
    async def version(self, ctx) -> any:

        # Grab git information
        last_commits = self.core.fetch_output(["git", "log", "-n", "5", "--oneline", "--pretty=format:'%s <%an>'"]).replace("'", "")
        curnt_branch = self.core.fetch_output("git branch --show-current")
        lastmodified = self.core.fetch_output("git log -1 --pretty=format:%cd")

        # Construct embed
        embed = self.core.embed(
            title = f"Prism v{__version__} - Build Info",
            description = f"Current branch: `{curnt_branch}`",
            url = self.github_repo,
            footer = ctx
        )
        embed.add_field(name = "Last 5 commits", value = f"```\n{last_commits}\n```", inline = False)
        embed.add_field(name = "Last modified", value = f"```\n{lastmodified}\n```", inline = False)
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Version(bot))
