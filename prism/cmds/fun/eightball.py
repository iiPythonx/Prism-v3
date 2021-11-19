# Copyright 2021 iiPython

# Modules
import random
from discord.ext import commands
from discord.commands import Option

# Command class
class Eightball(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self._8ball_responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes, definitely.",
            "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
            "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
            "Better not tell you now", "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.",
            "Very doubtful."
        ]

    @commands.slash_command(description = "Ask the magic eightball a question.")
    async def eightball(self, ctx, *, question: Option(str, "What you want to ask the eightball")) -> any:
        response = random.choice(self._8ball_responses)

        # Try to format the question
        if not question.endswith("?"):
            question += "?"

        question = question[0].upper() + question[1:]
        question = question.replace(" i ", " I ")

        # Send response
        return await ctx.respond(embed = self.core.embed(title = question, description = f"> {response}"))

# Link
def setup(bot) -> None:
    return bot.add_cog(Eightball(bot))
