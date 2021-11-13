"""
    Development related commands for Prism
    Copyright (c) 2021 iiPython
"""

from .dev import Dev

def setup(bot) -> None:
    bot.add_cog(Dev(bot))
