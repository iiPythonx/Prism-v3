"""
    Economy related commands for Prism
    Copyright (c) 2021 iiPython
"""

from .economy import Economy

def setup(bot) -> None:
    bot.add_cog(Economy(bot))
