# Copyright 2021 iiPython

# Modules
import os
import random
import discord
from PIL import Image
from discord.ext import commands
from discord.commands import Option

# Command class
class Triggered(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self.im = self.core.images

    @commands.slash_command(description = "Is it just me, or are they triggered?")
    async def triggered(self, ctx, user: Option(discord.Member, "The user to make triggered", required = False)) -> any:
        user = user or ctx.author

        # Initialization
        image = self.im.imagefromURL(user.avatar.url).resize((216, 216), Image.ANTIALIAS)
        text = Image.open(os.path.join(self.core.asset_dir, "img/triggered.jpg"))

        # Animating
        canvas = Image.new(mode = "RGB", size = image.size, color = (0, 0, 0))
        images, num = [], 0
        while num < 100:
            canvas.paste(image, (random.randint(-4, 4), random.randint(-4, 4)))
            images.append(canvas)
            canvas.paste(text, (random.randint(-4, 4), (216 - 39) + (random.randint(-4, 4))))
            canvas = Image.new(mode = "RGB", size = image.size, color = (0, 0, 0))
            num += 5

        # Compiling to GIF
        data = self.im.compileGIF(images, 3)

        # Send the image
        return await ctx.respond(file = discord.File(data, "triggered.gif"))

# Link
def setup(bot) -> None:
    return bot.add_cog(Triggered(bot))
