# Copyright 2021 iiPython

# Modules
from prism.config import config
from discord.ext import commands
from discord.commands import Option

# Command class
class Help(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self._cat_long_map = {"misc": "Miscellaneous", "fun": "Entertainment", "currency": "Economy", "image": "Images"}

    def _fetch_attrs(self) -> list:
        attrs = []
        for cmd_id, command in self.bot.application_commands.items():
            if hasattr(command.cog, "hidden") and command.cog.hidden:
                continue

            attr = {"name": command.name, "desc": command.description, "cat": command.category}
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

    @commands.slash_command(description = "The Prism help command.", category = "misc")
    async def help(self, ctx, query: Option(str, "The query to search for", required = False) = None) -> any:
        embed = self.core.embed(footer = ctx)
        embed.set_thumbnail(url = self.bot.user.avatar.url)

        # Fetch command list
        attrs = self._fetch_attrs()
        categories = self._gen_categories(attrs)

        # Construct primary help command
        if query is None:
            embed.title = "Prism v3"
            embed.add_field(name = "Categories", value = f"> {self.core.format_list(categories)}", inline = False)
            embed.add_field(name = "Commands", value = "> /help [category]", inline = False)
            embed.add_field(
                name = "Credits",
                value = f"> {self.core.format_list([self.bot.owner.split('#')[0]] + config.get(['admins', 'friends']))}",
                inline = False
            )

        else:
            query = query.lower()

            # Check categories
            if query in categories:

                # Create embed
                embed.title = f"{self._cat_long_map[query]} Commands"
                embed.add_field(name = "Commands", value = f"> {self.core.format_list(self._get_cat_commands(query, attrs))}", inline = False)

            # Check commands
            for attr in attrs:
                if attr["name"] == query:

                    # Create embed
                    embed.title = f"Command Info - {query}"
                    embed.add_field(name = "Description", value = f"> {attr['desc']}", inline = False)
                    embed.add_field(name = "Category", value = f"> {self._cat_long_map[attr['cat']]} ({attr['cat']})", inline = False)

            # Error handle
            if not embed.title:
                return await ctx.respond(embed = self.core.error("No results found."))

        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Help(bot))
