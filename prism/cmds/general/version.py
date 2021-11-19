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
        last_commit = self.core.fetch_output("git log -1 --pretty=format:%B")
        last_author = self.core.fetch_output(["git", "log", "-1", "--pretty=format:'%an <%ae>"]).strip("'")
        curr_branch = self.core.fetch_output("git branch --show-current")
        last_modify = self.core.fetch_output("git log -1 --pretty=format:%cd")
        filesmodify = len(self.core.fetch_output("git diff --name-only HEAD HEAD~1").split("\n"))

        # Construct embed
        embed = self.core.embed(
            title = f"Prism v{__version__} - Build Info",
            description = f"Current branch: `{curr_branch}`",
            url = self.github_repo,
            footer = ctx
        )
        embed.add_field(name = "Last commit", value = f"```\n\"{last_commit}\"\n(by {last_author})\n```", inline = False)
        embed.add_field(name = "Last modified", value = f"```\n{last_modify}\n{filesmodify} file(s) changed.\n```", inline = False)
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Version(bot))
