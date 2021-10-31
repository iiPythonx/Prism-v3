# Copyright 2021 iiPython

# Modules
import math
import random
import discord
from discord.ext import commands

# Interaction handler
class WorkButtons(discord.ui.View):
    def __init__(self, ctx, problem: tuple) -> None:
        super().__init__()
        self.ctx, self.bot, self.problem = ctx, ctx.bot, problem

        # Create buttons
        self.btns = {}
        for ans in problem[1]:
            btn = discord.ui.Button(label = ans)
            btn.callback = self.callback

            self.btns[btn.custom_id] = btn.label
            self.add_item(btn)

    async def callback(self, inter) -> None:
        if inter.user != self.ctx.author:
            return

        self.stop()
        cid = inter.data["custom_id"]
        if cid not in self.btns:
            return

        # Resolve button colors
        for item in self.children:
            if int(item.label) != self.problem[2]:
                item.style = discord.ButtonStyle.red

            else:
                item.style = discord.ButtonStyle.green

        # Handle working balance
        got_right = self.problem[2] == int(self.btns[cid])
        if not got_right:

            # Cooldown
            self.bot.cooldowns.add_cooldown("work", self.ctx.author, 900)

            # Construct embed
            embed = self.bot.core.embed(
                title = "That's not right...",
                description = f"The correct answer was {self.problem[2]}."
            )
            embed.set_footer(text = "| Come back in 15 minutes.", icon_url = self.ctx.author.avatar.url)
            return await inter.response.edit_message(embed = embed, view = self)

        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", self.ctx.author.id)):
            return await self.ctx.send(embed = self.core.noacc(self.ctx, self.ctx.author))

        bal = db.get(("userid", self.ctx.author.id), "balance")
        try:
            gain = round(math.ceil(bal / 100) * max(math.log(math.floor(bal / 100)) * 0.5, 0) + 500)

        except ValueError:
            gain = 500

        db.update({"balance": bal + gain}, ("userid", self.ctx.author.id))

        # Cooldown
        self.bot.cooldowns.add_cooldown("work", self.ctx.author, 3600)

        # Construct embed
        embed = self.bot.core.embed(
            title = "Correct!",
            description = f"Coins gained: {self.bot.core.format_coins(gain)} coins\nNew balance: {self.bot.core.format_coins(bal + gain)} coins"
        )
        embed.set_footer(text = "| Come back in an hour.", icon_url = self.ctx.author.avatar.url)
        return await inter.response.edit_message(embed = embed, view = self)

# Command class
class Work(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "work", "desc": "Allows you to work for money.", "cat": "currency", "usage": "work"}

    def generate_problem(self) -> list:
        nums = []
        while len(nums) != 2:
            n = random.randint(1, 20)
            if n not in nums:
                nums.append(n)

        n1, n2 = nums
        operator, op_map = random.choice(["+", "-"]), {
            "+": lambda n1, n2: n1 + n2,
            "-": lambda n1, n2: n1 - n2
        }

        # Generate two incorrect answers
        correct, incorrects = op_map[operator](n1, n2), []
        while len(incorrects) != 2:
            ans = random.choice(range(correct - 3, correct + 3))
            if ans not in incorrects and ans not in [n1, n2, correct]:
                incorrects.append(ans)

        # Return problem data
        return [f"{n1} {operator} {n2}", incorrects + [correct], correct]

    @commands.command(pass_context = True)
    async def work(self, ctx) -> any:
        if self.bot.cooldowns.on_cooldown("work", ctx.author):
            return await ctx.send(embed = self.bot.cooldowns.cooldown_text("work", ctx.author))

        problem = self.generate_problem()

        # Create embed
        embed = self.core.embed(title = f"What is {problem[0]}?", description = "You have 5 seconds to answer.")
        return await ctx.send(
            embed = embed,
            view = WorkButtons(ctx, problem)
        )

# Link
def setup(bot) -> None:
    return bot.add_cog(Work(bot))
