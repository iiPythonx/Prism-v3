# Copyright 2021 iiPython

# Modules
import math
import random
import discord
import asyncio
import requests
import urllib.parse
from typing import Union
from discord.ext import commands
from discord.commands import Option
from pyfiglet import Figlet, FigletError

# Command class
class Fun(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self._dict_url = "https://api.urbandictionary.com/v0/define?term={}"
        self._8ball_responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes, definitely.",
            "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
            "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
            "Better not tell you now", "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.",
            "Very doubtful."
        ]
        self._rps_resp = ["🪨", "📰", "✂️"]
        self._rps_resdict = {-1: "You won!", 0: "Tie!", 1: "I won!"}

        self._cooldown_times = {"guess": (60 * 60) * 5}

    def rps_pick(self) -> str:
        return random.choice(self._rps_resp)

    def rps_rate(self, first: str, second: str) -> int:
        if first == second:
            return 0

        elif first == "🪨" and second == "✂️":
            return -1

        elif first == "📰" and second == "🪨":
            return -1

        elif first == "✂️" and second == "📰":
            return -1

        else:
            return 1

    def search(self, phrase: str) -> Union[dict, None]:
        try:
            req = requests.get(
                self._dict_url.format(urllib.parse.quote(phrase.lower())),
                headers = {"Content-Type": "application/json"},
                timeout = 2
            ).json()
            if not req["list"]:
                return None

            return max(req["list"], key = lambda d: d["thumbs_up"])

        except Exception:
            raise ConnectionError

    def text_scramble(self, text: str) -> str:
        chars = list(text)
        random.shuffle(chars)
        return "".join(chars)

    def text_caps(self, text: str) -> str:
        return "".join([getattr(char, random.choice(["lower", "upper"]))() for char in list(text)])

    @commands.slash_command(description = "Turns text into ASCII art.", category = "fun")
    async def ascii(
        self,
        ctx,
        text: Option(str, "The text to ASCIIify"),
        font: Option(
            str,
            "The font to use",
            choices = ["starwars", "doom", "goofy", "basic", "block", "chunky", "cricket"],  # noqa
            required = False,
            default = "starwars"  # noqa
        )
    ) -> any:
        try:
            result = Figlet(font = font).renderText(text)
            try:
                return await ctx.respond(f"```\n{result}\n```")

            except discord.HTTPException:
                return await ctx.respond(embed = self.core.error("Text is too long."))

        except FigletError:
            return await ctx.respond(embed = self.core.error("Error parsing text."))

    @commands.slash_command(description = "Searches Urban Dictionary for a phrase.", category = "fun")
    @commands.is_nsfw()
    async def dict(self, ctx, phrase: Option(str, "The phrase to lookup")) -> any:
        try:
            data = self.search(phrase)
            if data is None:
                return await ctx.respond(embed = self.core.error("No results found."))

            try:
                return await ctx.respond(embed = self.core.embed(title = data["word"], description = data["definition"], url = data["permalink"], footer = ctx))

            except discord.HTTPException:
                return await ctx.respond(embed = self.core.error("The definition is too long to send."))

        except ConnectionError:
            return await ctx.respond(embed = self.core.error("Failed to connect to Urban Dictionary.\nTry again later."))

    @commands.slash_command(description = "Ask the magic eightball a question.", category = "fun")
    async def eightball(self, ctx, *, question: Option(str, "What you want to ask the eightball")) -> any:
        response = random.choice(self._8ball_responses)

        # Try to format the question
        if not question.endswith("?"):
            question += "?"

        question = question[0].upper() + question[1:]
        question = question.replace(" i ", " I ")

        # Send response
        return await ctx.respond(embed = self.core.embed(title = question, description = f"> {response}"))

    @commands.slash_command(description = "Earn coins for guessing the right number.", category = "fun")
    async def guess(self, ctx) -> any:
        if self.bot.cooldowns.on_cooldown("guess", ctx.author):
            return await ctx.respond(embed = self.bot.cooldowns.cooldown_text("guess", ctx.author))

        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author))

        # Initialization
        max_num = random.randint(7, 13)
        number = random.randint(1, max_num)

        bal = db.get(("userid", ctx.author.id), "balance")

        # Calculate gain
        try:
            coins = round(math.ceil(bal / 100) * max(math.log(math.floor(bal / 100)) * 0.5, 0) + 500) * 3

        except ValueError:
            coins = 1500

        # Send embed
        embed = self.core.embed(
            title = "Think you can guess it?",
            description = f"I'm thinking of a number between 1 and {max_num}.\nIf you guess it, I'll give you {self.core.format_coins(coins)} coins. You have 5 seconds.\n\nTo guess, simply type the number in chat.",
            footer = ctx
        )
        msg = await ctx.respond(embed = embed)

        # Wait for number
        try:
            m = await self.core.get_message(ctx)
            try:
                if m is None:
                    self.bot.cooldowns.add_cooldown("guess", ctx.author, self._cooldown_times["guess"])
                    return await ctx.respond(embed = self.core.error("That doesn't look like a number."))

                m = int(m)
                if m != number:
                    self.bot.cooldowns.add_cooldown("guess", ctx.author, self._cooldown_times["guess"])
                    return await ctx.respond(embed = self.core.error(f"Sorry, I was thinking of `{number}`."))

            except ValueError:
                self.bot.cooldowns.add_cooldown("guess", ctx.author, self._cooldown_times["guess"])
                return await ctx.respond(embed = self.core.error("Woops, that isn't a number."))

        except asyncio.exceptions.TimeoutError:
            self.bot.cooldowns.add_cooldown("guess", ctx.author, self._cooldown_times["guess"])
            return await ctx.respond(embed = self.core.error("You didn't guess in time!"))

        # Update balance
        db.update({"balance": bal + coins}, ("userid", ctx.author.id))

        # Success embed
        embed = self.core.embed(
            title = "Congratulations!",
            description = f"You got the number right, it was `{number}`.\n`{coins}` coins have been added to your balance.",
            footer = ctx
        )
        await msg.edit(embed = embed)
        return self.bot.cooldowns.add_cooldown("guess", ctx.author, self._cooldown_times["guess"])

    @commands.slash_command(description = "Gives you a random 'never have i ever' question.", category = "fun")
    async def neverhaveiever(self, ctx) -> any:
        return await ctx.respond(embed = self.core.small_embed("Never have I ever " + random.choice([
            "walked a dog", "went to a bar", "made some ascii text",
            "peed in a pool", "worn crocs", "walked a tight-rope",
            "been chased by a dog", "farted in an elevator",
            "used the bathroom in darkness", "pretended to be a burglar",
            "pranked my parents", "kissed a stranger", "dyed my hair the wrong color",
            "tried watching television upside down", "killed a pet by accident",
            "been trapped in an elevator", "driven a car naked",
            "woken someone up by snoring", "given someone a black eye"
        ]) + "."))

    @commands.slash_command(description = "Play Rock Paper Scissors.", category = "fun")
    async def rps(self, ctx) -> any:
        await ctx.respond(embed = self.core.embed(title = "Now playing Rock Paper Scissors..."))
        results = []
        for i in range(3):
            em = self.core.embed(title = f"Round {i + 1}")
            try:
                msg = await ctx.send(embed = em)
                reaction = await self.core.wait_for_reaction(ctx, msg, self._rps_resp)

            except asyncio.exceptions.TimeoutError:
                return await ctx.respond(embed = self.core.error("You didn't respond in time."))

            ans = self.rps_pick()
            reaction = reaction[0].emoji
            results.append(self.rps_rate(reaction, ans))

            em.title += f" - {self._rps_resdict[results[-1]]}"
            em.description = f"Me: {ans} | You: {reaction}"
            await msg.edit(embed = em)

        # Final embed
        title = ("You won!" if results.count(-1) > results.count(1) else "") or ("I won!" if results.count(1) > results.count(-1) else "") or "Tie!"
        embed = self.core.embed(
            title = title,
            description = f"I got {results.count(1)}/3; you got {results.count(-1)}/3.",
            footer = ctx
        )

        return await ctx.send(embed = embed)

    @commands.slash_command(description = "Sock somebody for some easy coins.", category = "fun")
    async def sock(self, ctx, *, user: Option(discord.Member, "The user you wish to sock")) -> any:
        if user == ctx.author:
            return await ctx.respond(embed = self.core.error("Why would you want to sock yourself?"))

        # Handle cooldowns
        if self.bot.cooldowns.on_cooldown("sock", ctx.author):
            return await ctx.respond(embed = self.bot.cooldowns.cooldown_text("sock", ctx.author))

        # Handle database
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", user.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, user))

        elif not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author))

        # Handle logic
        if random.randint(1, 10) in range(8):
            obal = db.get(("userid", user.id), "balance")
            lbal = db.get(("userid", ctx.author.id), "balance")

            # Grab percentage
            percent = random.randint(3, 7)
            amount = round(obal / (100 / percent))

            # Update balances
            db.update({"balance": obal - amount}, ("userid", user.id))
            db.update({"balance": lbal + amount}, ("userid", ctx.author.id))

            # Give our nice embed
            uname, oname = self.core.frmt_name(ctx.author), self.core.frmt_name(user)
            await ctx.respond(
                embed = self.core.embed(
                    title = random.choice(["rekt", "#pwned", "Imagine getting socked", "Impressive", "GG"]),
                    description = f"{uname} socked {oname} and got away with {self.core.format_coins(amount)} coins."
                )
            )

        else:
            await ctx.respond(embed = self.core.error("Nice try kiddo. You missed your shot."))

        return self.bot.cooldowns.add_cooldown("sock", ctx.author, 300)

    @commands.slash_command(description = "Mess around with text in weird ways.", category = "fun")
    async def text(self, ctx, action: Option(str, "The action to perform", choices = ["scramble", "caps"]), text: Option(str, "The text to mess with")) -> any:  # noqa
        try:
            return await ctx.respond({
                "scramble": self.text_scramble,
                "caps": self.text_caps
            }[action](text))

        except discord.HTTPException:
            return await ctx.respond(embed = self.core.error("Your text is too long."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Fun(bot))
