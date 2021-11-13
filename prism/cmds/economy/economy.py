# Copyright 2021 iiPython

# Modules
import math
import random
import discord
import iipython as ip
from discord.ext import commands
from discord.commands import Option
from prism.core.banks import get_bank_balance

# Work interactions
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
            return await self.ctx.respond(embed = self.core.noacc(self.ctx, self.ctx.author))

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
class Economy(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self.people = [
            {"name": "Rick Astley", "quote": lambda: "never gonna " + random.choice(["give you up", "let you down", "run around and desert you"])},
            {"name": "iiPython", "quote": lambda: random.choice(["go get a job", "don't spend it on socks", "linux > windows"])},
            {"name": "Dream", "quote": lambda: "*speedrunning music intensifies*"},
            {"name": "Elon Musk", "quote": lambda: random.choice(["buy a tesla pls", "rocket ship go brrrRRR"])},
            {"name": "Bill Gates", "quote": lambda: "i very rich"},
            {"name": "Donald Trump", "quote": lambda: "IM GONNA BUILD A WALL"},  # Slightly political, but come on it's not that bad
            {"name": "Steve Jobs", "quote": lambda: "have you bought the iPhone 14S Pro Max Lite Premium SE yet?"}
        ]
        self._mults = {
            3: ["❌"],
            4: ["7️⃣", "🪙"],
            5: ["🍒"]
        }
        self._items = ip.normalize(*list(self._mults[i] for i in self._mults))

    def pick(self) -> str:
        return random.choice(self._items)

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

    @commands.slash_command(description = "Checks somebodies account balance.", category = "currency")
    async def balance(self, ctx, user: Option(discord.Member, "The user to check the balance of", required = False) = None) -> any:
        user = user or ctx.author

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", user.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, user))

        bal = db.get(("userid", user.id), "balance")
        bank_bal = get_bank_balance(user.id)

        # Handle embed
        embed = self.core.embed(title = str(user), footer = ctx)
        embed.add_field(name = "Balance", value = f"{self.core.format_coins(bal)} coin(s)", inline = False)
        embed.add_field(name = "Bank Balance", value = f"{self.core.format_coins(bank_bal)} coin(s)", inline = False)
        return await ctx.respond(embed = embed)

    @commands.slash_command(description = "Beg the rich for money.", category = "currency")
    async def beg(self, ctx) -> any:
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author))

        elif self.bot.cooldowns.on_cooldown("beg", ctx.author):
            return await ctx.respond(embed = self.bot.cooldowns.cooldown_text("beg", ctx.author))

        bal = db.get(("userid", ctx.author.id), "balance")
        earn = random.randint(84, 213)

        db.update({"balance": bal + earn}, ("userid", ctx.author.id))
        self.bot.cooldowns.add_cooldown("beg", ctx.author, 60)

        # Handle embed
        person = random.choice(self.people)
        embed = self.core.embed(
            title = f"{person['name']} gave you `{earn}` coins.",
            description = f"\"{person['quote']()}\"",
            footer = ctx
        )
        return await ctx.respond(embed = embed)

    @commands.slash_command(description = "Creates a Prism account.", category = "currency")
    async def create(self, ctx) -> any:
        db = self.bot.db.load_db("users")
        if db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.error("You already have a Prism account."))

        db.create((ctx.author.id, 100, "", self.core.storage["accent"]))
        return await ctx.respond(embed = self.core.small_embed(":tada: You now have a Prism account."))

    @commands.slash_command(description = "Get free coins everyday.", category = "currency")
    async def daily(self, ctx) -> any:
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author))

        elif self.bot.cooldowns.on_cooldown("daily", ctx.author):
            return await ctx.respond(embed = self.bot.cooldowns.cooldown_text("daily", ctx.author))

        bal = db.get(("userid", ctx.author.id), "balance")
        try:
            earn = round(math.ceil(bal / 100) * max(math.log(math.floor(bal / 100)) * 0.2, 0) + 400)

        except ValueError:
            earn = 300

        db.update({"balance": bal + earn}, ("userid", ctx.author.id))
        self.bot.cooldowns.add_cooldown("daily", ctx.author, 86400)

        # Handle embed
        embed = self.core.small_embed(f"You redeemed `{self.core.format_coins(earn)}` coin(s).", footer = ctx)
        return await ctx.respond(embed = embed)

    @commands.slash_command(description = "Pays another user using coins from your balance.", category = "currency")
    async def pay(self, ctx, user: Option(discord.Member, "The user you wish to pay."), amount: Option(str, "The amount to pay.")) -> any:
        if user == ctx.author:
            return await ctx.respond(embed = self.core.error("You cannot pay yourself."))

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", user.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, user))

        bal = db.get(("userid", ctx.author.id), "balance")

        # Check amount
        try:
            amount = int(amount)

        except ValueError:
            try:
                amount = self.core.amountstr_to_bal(amount, bal)

            except ValueError:
                return await ctx.respond(embed = self.core.error("Invalid amount specified."))

        if amount < 1:
            return await ctx.respond(embed = self.core.error("You need to pay at least 1 coin."))

        elif amount > bal:
            return await ctx.respond(embed = self.core.error("You don't have that many coins."))

        # Handle transaction
        end_user_bal = db.get(("userid", user.id), "balance")
        end_user_bal += amount
        bal -= amount

        db.update({"balance": bal}, ("userid", ctx.author.id))
        db.update({"balance": end_user_bal}, ("userid", user.id))

        # Handle embed
        embed = self.core.embed(
            title = f"{self.core.emojis['checkmark']} | Transaction complete.",
            description = f"Transferred: {self.core.format_coins(amount)} coin(s) | To: {user.mention}\nNew balance: {self.core.format_coins(bal)}",
            footer = ctx
        )
        return await ctx.respond(embed = embed)

    @commands.slash_command(description = "Spin some slot machines and earn some coins (or lose some).", category = "currency")
    async def slots(self, ctx, bet: Option(int, "The amount you want to bet.")) -> any:
        if self.bot.cooldowns.on_cooldown("slots", ctx.author):
            return await ctx.respond(embed = self.bot.cooldowns.cooldown_text("slots", ctx.author))

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author))

        bal = db.get(("userid", ctx.author.id), "balance")
        if bet < 100:
            return await ctx.respond(embed = self.core.error("You need to bet at least 100 coins."))

        elif bet > bal:
            return await ctx.respond(embed = self.core.error("You don't have that many coins."))

        # Handle results
        picks = [self.pick() for i in ip.xrange(1, 3)]
        results, earn = "  |  ".join(picks), 0
        for mult in self._mults:
            brk = False
            for emoji in self._mults[mult]:
                if results.count(emoji) == 3:
                    earn = bet * mult
                    brk = True
                    break

            if brk:
                break

        # Save data
        db.update({"balance": bal + (earn or -bet)}, ("userid", ctx.author.id))
        self.bot.cooldowns.add_cooldown("slots", ctx.author, 120)

        # Send embed
        return await ctx.respond(embed = self.core.embed(
            title = results,
            description = f"{f'You won `{self.core.format_coins(earn)}`' if earn else f'You lost your `{self.core.format_coins(bet)}`'} coin(s)."
        ))

    @commands.slash_command(description = "Allows you to work for money.", category = "currency")
    async def work(self, ctx) -> any:
        if self.bot.cooldowns.on_cooldown("work", ctx.author):
            return await ctx.respond(embed = self.bot.cooldowns.cooldown_text("work", ctx.author))

        problem = self.generate_problem()

        # Create embed
        embed = self.core.embed(title = f"What is {problem[0]}?", description = "You have 5 seconds to answer.")
        return await ctx.respond(
            embed = embed,
            view = WorkButtons(ctx, problem)
        )

# Link
def setup(bot) -> None:
    return bot.add_cog(Economy(bot))
