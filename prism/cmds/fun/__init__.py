"""
    Entertainment related commands for Prism
    Copyright (c) 2021 iiPython
"""

from .fun import Fun

def setup(bot) -> None:
    bot.add_cog(Fun(bot))
