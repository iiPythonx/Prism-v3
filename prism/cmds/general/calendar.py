# Copyright 2021-xx iiPython

# Modules
import discord
import calendar
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

# Command class
class Calendar(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self.agenda_store = {}

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

    @commands.slash_command(description = "Control your user agenda")
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

    @commands.slash_command(description = "Shows a calendar of the month")
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

# Link
def setup(bot) -> None:
    return bot.add_cog(Calendar(bot))
