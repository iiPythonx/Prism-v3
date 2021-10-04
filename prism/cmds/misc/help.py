# Copyright 2021 iiPython

# Modules
from prism.config import config
from discord.ext import commands

# Command class
class Help(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "help", "desc": "The help command, allowing you to get basic information.", "cat": "misc", "usage": "help [command/alias/category]"}

        self._cat_long_map = {"misc": "Miscellaneous", "fun": "Entertainment", "currency": "Economy", "image": "Images"}

    def _fetch_attrs(self) -> list:
        attrs = []
        for command in self.bot.commands:
            if hasattr(command.cog, "hidden") and command.cog.hidden:
                continue

            attr = command.cog.attr
            attr["aliases"] = command.aliases
            attrs.append(attr)

        return attrs

    def _gen_categories(self, attrs: dict) -> list:
        categories = []
        for attr in attrs:
            if attr["cat"] not in categories:
                categories.append(attr["cat"])

        return categories

    def _get_cat_commands(self, category: str, attrs: list) -> list:
        cmds = []
        for attr in attrs:
            if attr["cat"] == category:
                cmds.append(attr["name"])

        return cmds

    @commands.command(pass_context = True, aliases = ["info"])
    async def help(self, ctx, query: str = None) -> any:

        # Construct embed
        embed = self.core.embed(footer = ctx)
        embed.set_thumbnail(url = self.bot.user.avatar.url)

        # Fetch command list
        attrs = self._fetch_attrs()
        categories = self._gen_categories(attrs)

        # Construct primary help command
        if query is None:
            embed.title = "Prism v3"
            embed.add_field(name = "Categories", value = f"> {self.core.format_list(categories)}", inline = False)
            embed.add_field(name = "Commands", value = f"> {ctx.prefix}help [category]", inline = False)
            embed.add_field(
                name = "Credits",
                value = f"> {self.core.format_list([config.get('owner').split('#')[0]] + config.get('friends'))}",
                inline = False
            )

        else:

            # Check query
            query = query.lower()

            # Check categories
            if query in categories:

                # Create embed
                embed.title = f"{self._cat_long_map[query]} Commands"
                embed.add_field(name = "Commands", value = f"> {self.core.format_list(self._get_cat_commands(query, attrs))}", inline = False)

            # Check commands
            for attr in attrs:
                if attr["name"] == query or query in attr["aliases"]:
                    if query in attr["aliases"]:
                        query = attr["name"]

                    # Create embed
                    embed.title = f"Command Info - {query}"
                    embed.add_field(name = "Description", value = f"> {attr['desc']}", inline = False)
                    embed.add_field(name = "Category", value = f"> {self._cat_long_map[attr['cat']]} ({attr['cat']})", inline = False)
                    if attr["aliases"]:
                        embed.add_field(name = "Aliases", value = f"> {self.core.format_list(attr['aliases'])}", inline = False)

                    embed.add_field(name = "Usage", value = f"> {attr['usage']}", inline = False)

            # Error handle
            if not embed.title:
                return await ctx.send(embed = self.core.error("No results found."))

        return await ctx.send(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Help(bot))
