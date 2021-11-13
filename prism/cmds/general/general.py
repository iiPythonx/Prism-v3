# Copyright 2021 iiPython

# Modules
import os
import psutil
import discord
import calendar
from prism import __version__
from datetime import datetime
from discord.ext import commands
from discord.commands import Option
from prism.core.models import Paginator

# Agenda pageinator class
class Agenda(Paginator):
    def create_page(self, page: int) -> discord.Embed:
        embed = self.core.embed(title = f"{self.core.frmt_name(self.ctx.author)}'s Agenda", footer = self.ctx)
        for item in self.pages[page]:
            embed.add_field(
                name = f"{(5 * page) + (self.pages[page].index(item) + 1)}. **{item['text']}**",
                value = f"Added at {item['added_at']}",
                inline = False
            )

        return embed

# Invite handler
class InviteButton(discord.ui.View):
    def __init__(self, url: str) -> None:
        super().__init__()
        self.invite.url = url

    @discord.ui.button(label = "Invite", url = "")
    async def invite(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        return

# Command class
class General(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self.agenda_store = {}
        self.github_repo = "https://github.com/ii-Python/Prism-v3"
        self._key_checks = {"accent": lambda v: self.core.color(v)}

    def _add_agenda_item(self, userid: int, text: str) -> None:
        data = {"text": text, "added_at": datetime.utcnow().strftime("%H:%M:%S UTC")}
        if userid not in self.agenda_store:
            self.agenda_store[userid] = [data]
            return

        self.agenda_store[userid].append(data)

    def _remove_agenda_item(self, userid: int, aid: str) -> None:
        if userid not in self.agenda_store:
            return

        try:
            self.agenda_store[userid].remove(self.agenda_store[userid][int(aid) - 1])

        except Exception:
            raise ValueError

    def chunk_items(self, items: list) -> list:
        for i in range(0, len(items), 5):
            yield items[i:i + 5]

    def format_sectors(self, lines: list) -> str:
        return "".join("> " + line + "\n" for line in lines)[:-1]

    @commands.slash_command(description = "Control your user agenda", category = "misc")
    async def agenda(
        self,
        ctx,
        action: Option(str, "The action to perform", choices = ["list", "add", "remove", "clear"]),  # noqa
        text: Option(str, "The agenda text", required = False) = None,
        agenda_id: Option(str, "The agenda ID to remove", required = False) = None
    ) -> any:
        if action == "add":
            if text is None:
                return await ctx.respond(embed = self.core.error("You need to provide text for your agenda item."))

            elif text in [a["text"] for a in self.agenda_store.get(ctx.author.id, [])]:
                return await ctx.respond(embed = self.core.error("You already have an agenda for that."))

            elif len(self.agenda_store.get(ctx.author.id, [])) == 20:
                return await ctx.respond(embed = self.core.error("You have reached the maximum agenda limit."))

            self._add_agenda_item(ctx.author.id, text)
            return await ctx.respond(embed = self.core.small_embed("Successfully added agenda item."))

        elif action == "remove":
            if agenda_id is None:
                return await ctx.respond(embed = self.core.error("No agenda ID provided to remove."))

            elif ctx.author.id not in self.agenda_store:
                return await ctx.respond(embed = self.core.error("You don't have any agenda items."))

            try:
                self._remove_agenda_item(ctx.author.id, agenda_id)
                if not self.agenda_store[ctx.author.id]:
                    del self.agenda_store[ctx.author.id]

            except ValueError:
                return await ctx.respond(embed = self.core.error("Invalid agenda ID."))

            return await ctx.respond(embed = self.core.small_embed("Successfully removed agenda item."))

        elif action == "list":
            if not self.agenda_store.get(ctx.author.id, []):
                return await ctx.respond(embed = self.core.error("You don't have any agenda items."))

            paginator = Agenda(ctx, list(self.chunk_items(self.agenda_store[ctx.author.id])))
            return await ctx.respond(embed = paginator.create_page(0), view = paginator)

        elif action == "clear":
            if ctx.author.id not in self.agenda_store:
                return await ctx.respond(embed = self.core.error("You don't have any agenda items."))

            del self.agenda_store[ctx.author.id]
            return await ctx.respond(embed = self.core.small_embed("Successfully cleared agenda items."))

    @commands.slash_command(description = "Shows a calendar of the month", category = "misc")
    async def calendar(self, ctx) -> any:
        current, line = datetime.now(), ""
        lines = [
            f"{' ' * 11}{current.strftime('%B, %Y')}",
            " Sun. Mon. Tue. Wed. Thu. Fri. Sat.",
            "+----------------------------------+"
        ]
        dates = calendar.Calendar(calendar.SUNDAY).monthdatescalendar(current.year, current.month)
        for week in dates:
            for day in week:
                if line.count("|") == 7:
                    lines.append(line + "|")
                    line = ""

                sep = " " if day.day != current.day else "-"
                line += f"|{sep}{day.strftime('%d')}{sep}"

        lines.append("+----------------------------------+")
        text = "\n".join(lines)
        return await ctx.respond(embed = self.core.embed(title = f"{current.strftime('%B')}'s Calendar", description = f"```\n{text}\n```", footer = ctx))

    @commands.slash_command(description = "Customize your profile.", category = "misc")
    async def customize(self, ctx, option: Option(str, "The option you wish to change", choices = ["bio", "accent"]), value: Option(str, "The new value")) -> any:  # noqa
        try:
            if option in self._key_checks:
                self._key_checks[option](value)

        except Exception:
            return await ctx.respond(embed = self.core.error(f"Invalid value provided for `{option}`."))

        # Load database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.send(embed = self.core.noacc(ctx, ctx.author))

        db.update({option: value}, ("userid", ctx.author.id))

        # Finish up
        return await ctx.respond(embed = self.core.small_embed("Profile successfully updated."))

    @commands.slash_command(description = "Lists someones inventory.", category = "misc")
    async def inventory(self, ctx, user: Option(discord.Member, "The user to view", required = False) = None) -> any:
        user = user or ctx.author

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", user.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, user))

        user_inv = self.core.inventory(user.id).items

        # Construct embed
        embed = self.core.embed(
            title = f"""{f"{self.core.frmt_name(user)}'s " if user != ctx.author else "Your "}Inventory""",
            description = self.core.format_list([f"{item}{f' (x{user_inv[item]})' if user_inv[item] > 1 else ''}" for item in user_inv]) if user_inv else "Nothing to display.",
            footer = ctx
        )
        embed.set_thumbnail(url = user.avatar.url)
        return await ctx.respond(embed = embed)

    @commands.slash_command(description = "Invite Prism to your server.", category = "misc")
    async def invite(self, ctx) -> any:
        url = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=2147609664&scope=applications.commands%20bot"
        return await ctx.respond(embed = self.core.small_embed("Invite Prism to your server."), view = InviteButton(url))

    @commands.slash_command(description = "Check the ping times", category = "misc")
    async def ping(self, ctx) -> any:

        # Test API ping
        tid = self.core.timer.start()
        inter = await ctx.respond(embed = self.core.embed(description = "**Checking ping...**"))

        api_ping = self.core.timer.end(tid, return_as = "ms", as_int = True)

        # Test bot ping
        bot_ping = round(self.bot.latency * 1000)

        # Show ping
        embed = self.core.embed(title = "Pong :ping_pong:", description = f"Bot: {bot_ping}ms | API: {api_ping}ms\nRoundtrip: {api_ping + bot_ping}ms")
        return await inter.edit_original_message(embed = embed)

    @commands.slash_command(description = "View somebodies profile.", category = "misc")
    async def profile(self, ctx, user: Option(discord.Member, "The user to view", required = False) = None) -> any:
        user = user or ctx.author

        # Load database
        db = self.bot.db.load_db("users")
        info = db.get(("userid", user.id))
        if info is None:
            return await ctx.respond(embed = self.core.noacc(ctx, user))

        # Construct embed
        embed = self.core.embed(
            title = str(user),
            description = f"\"{info['bio']}\"" if info["bio"] else "",
            footer = ctx,
            color = self.core.color(info["accent"])
        )
        embed.add_field(name = "Balance", value = f"{self.core.format_coins(info['balance'])} coin(s)", inline = False)
        embed.set_thumbnail(url = user.avatar.url)
        return await ctx.respond(embed = embed)

    @commands.slash_command(description = "Show Prism's system information.", category = "misc")
    async def stats(self, ctx) -> any:

        # Initialization
        vm = psutil.virtual_memory()
        mem_av = self.core.scale_size(vm.used, add_suffix = False)
        mem_tl = self.core.scale_size(vm.total)

        # Construct embed
        embed = self.core.embed(title = "System Statistics", footer = ctx)
        embed.add_field(
            name = "Bot info",
            value = self.format_sectors([
                f"Account: {self.bot.user}",
                f"Server count: {len(self.bot.guilds)} server(s)",
                f"Bot version - v{__version__}",
                f"[Library](https://github.com/ii-Python/discord) version: {discord.__version__}"
            ]),
            inline = False
        )
        embed.add_field(
            name = "System info",
            value = self.format_sectors([
                f"PID: {os.getpid()}",
                f"Memory usage: {mem_av}/{mem_tl}",
                f"Git version: {self.core.fetch_output('git --version', split = (' ', 2))}",
                f"Host: {self.core.fetch_output('uname -s -r -o')}"
            ]),
            inline = False
        )
        embed.set_thumbnail(url = self.bot.user.avatar.url)
        return await ctx.respond(embed = embed)

    @commands.slash_command(description = "Show Prism's version.", category = "misc")
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
    return bot.add_cog(General(bot))
