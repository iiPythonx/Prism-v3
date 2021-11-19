# Copyright 2021 iiPython

# Modules
import math
import json
import random
import discord
from discord.ext import commands
from discord.commands import Option

# Trivia handler
class TriviaView(discord.ui.View):
    def __init__(self, ctx, question: dict) -> None:
        super().__init__(timeout = 5)

        self.question = question
        self.ctx, self.bot, self.core = ctx, ctx.bot, ctx.bot.core

        # Create buttons
        self.btns = {}
        random.shuffle(question["choices"])
        for choice in question["choices"]:
            btn = discord.ui.Button(label = choice)
            btn.callback = self.callback

            self.btns[btn.custom_id] = btn.label
            self.add_item(btn)

    async def interaction_check(self, interaction) -> None:
        if interaction.user != self.ctx.author:
            return False

        return True

    async def on_timeout(self) -> None:
        return await self.message.edit_original_message(embed = self.core.error("You took too long to respond!"), view = None)

    async def callback(self, inter) -> None:
        self.stop()
        cid = inter.data["custom_id"]
        if cid not in self.btns:
            return

        # Resolve button colors
        for item in self.children:
            if item.label != self.question["answer"]:
                item.style = discord.ButtonStyle.red

            else:
                item.style = discord.ButtonStyle.green

        got_right = self.question["answer"] == self.btns[cid]
        if not got_right:
            embed = self.core.embed(
                title = "That's not right...",
                description = f"The correct answer was `{self.question['answer']}`.",
                footer = self.ctx
            )
            return await inter.response.edit_message(embed = embed, view = self)

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", self.ctx.author.id)):
            return await self.ctx.respond(embed = self.core.noacc(self.ctx, self.ctx.author))

        bal = db.get(("userid", self.ctx.author.id), "balance")
        try:
            gain = round(math.ceil(bal / 100) * max(math.log(math.floor(bal / 100)) * 0.05, 0) + 200)

        except ValueError:
            gain = 200

        db.update({"balance": bal + gain}, ("userid", self.ctx.author.id))

        # Construct embed
        embed = self.bot.core.embed(
            title = "Correct!",
            description = f"Coins gained: {self.bot.core.format_coins(gain)} coins\nNew balance: {self.bot.core.format_coins(bal + gain)} coins"
        )
        return await inter.response.edit_message(embed = embed, view = self)

# Command class
class Trivia(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        trivia_files = ["programming", "sports"]
        self.data = self.core.generate_data_dir(__file__)
        self.trivia = {}
        for file in trivia_files:
            file += ".json"
            with open(self.data.path(f"trivia/{file}"), "r") as f:
                self.trivia[file.removesuffix(".json")] = json.loads(f.read())

    @commands.slash_command(description = "Answer trivia questions for coins.", category = "fun")
    async def trivia(self, ctx, category: Option(str, "The category of trivia", choices = ["programming", "sports"])) -> any:  # noqa
        question = random.choice(self.trivia[category])

        # Send embed
        embed = self.core.embed(description = question["question"])
        embed.set_footer(text = "You have 5 seconds to answer.")

        view = TriviaView(ctx, question)
        view.message = await ctx.respond(
            embed = embed,
            view = view
        )

# Link
def setup(bot) -> None:
    return bot.add_cog(Trivia(bot))
