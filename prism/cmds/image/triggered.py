# Copyright 2021 iiPython

# Modules
import os
import random
import discord
from PIL import Image
from discord.ext import commands

# Command class
class Triggered(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.attr = {"name": "triggered", "desc": "Is it just me, or are they triggered?", "cat": "image", "usage": "triggered [user]"}

        self.im = self.bot.objects["img"]

    @commands.command(pass_context = True)
    async def triggered(self, ctx, user = None) -> any:
        user = self.core.get_user(ctx, user or ctx.author)
        if user is None:
            return await ctx.send(embed = self.core.nouser())

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
        return await ctx.send(file = discord.File(data, "triggered.gif"))

# Link
def setup(bot) -> None:
    return bot.add_cog(Triggered(bot))
