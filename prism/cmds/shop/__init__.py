"""
    Shop related commands for Prism
    Copyright (c) 2021 iiPython
"""

from .shop import Shop

def setup(bot) -> None:
    bot.add_cog(Shop(bot))
