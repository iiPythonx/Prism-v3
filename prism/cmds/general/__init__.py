"""
    General commands for Prism
    Copyright (c) 2021 iiPython
"""

from .general import General

def setup(bot) -> None:
    bot.add_cog(General(bot))
