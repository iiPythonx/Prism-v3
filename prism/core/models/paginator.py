# Copyright 2021-xx iiPython

# Modules
import discord

# Paginator class
class Paginator(discord.ui.View):
    def __init__(self, ctx, pages: list, page: int = 1) -> None:
        super().__init__()
        self.ctx = ctx
        self.bot = ctx.bot
        self.core = self.bot.core

        # Correct page number
        if page > len(pages):
            raise ValueError

        elif page < 1:
            raise ValueError

        self.pages = pages
        self.current_page = 0

        # Create buttons
        self.btns = {}
        if len(self.pages) > 1:
            for i in ["Prev", "Next"]:
                self.make_button(i)

    def make_button(self, text: str) -> None:
        btn = discord.ui.Button(label = text)
        btn.callback = self.callback
        self.btns[btn.custom_id] = text
        self.add_item(btn)

    def create_page(self, page: int) -> discord.Embed:
        raise RuntimeError("No create_page has been defined for this Paginator.")

    async def load_page(self, inter: discord.Interaction, page: int) -> None:
        return await inter.message.edit(embed = self.create_page(page))

    async def callback(self, inter: discord.Interaction) -> None:
        if inter.user != self.ctx.author:
            return

        button = self.btns[inter.data["custom_id"]]
        if button == "Prev" and self.current_page > 0:
            self.current_page -= 1
            return await self.load_page(inter, self.current_page)

        elif button == "Next" and self.current_page < (len(self.pages) - 1):
            self.current_page += 1
            return await self.load_page(inter, self.current_page)
