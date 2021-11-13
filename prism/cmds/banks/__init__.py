"""
    Bank related commands for Prism
    Copyright (c) 2021 iiPython
"""

from .banks import Banks

def setup(bot) -> None:
    bot.add_cog(Banks(bot))
