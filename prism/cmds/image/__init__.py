"""
    Image related commands for Prism
    Copyright (c) 2021 iiPython
"""

from .image import Image

def setup(bot) -> None:
    bot.add_cog(Image(bot))
