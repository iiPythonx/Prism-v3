# Copyright 2021 iiPython

# Modules
import traceback
from discord.ext import commands
from prism.utils.timer import timer

# Command class
class Module(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.hidden = True

    def load_module(self, module: str, reloaded: bool = False) -> str:
        try:
            self.bot.load_extension(module)
            return f"[loaded '{module}']" if not reloaded else f"[reloaded '{module}']"

        except Exception as Error:
            return f"[failed to load module '{module}']\n'{Error}'\n{''.join(_ for _ in traceback.StackSummary.from_list(traceback.extract_tb(Error.__traceback__)).format())}"

    def unload_module(self, module: str) -> str:
        try:
            self.bot.unload_extension(module)
            return f"[unloaded '{module}']"

        except Exception as Error:
            return f"[failed to unload module '{module}']\n'{Error}'\n{''.join(_ for _ in traceback.StackSummary.from_list(traceback.extract_tb(Error.__traceback__)).format())}"

    @commands.command(pass_context = True)
    @commands.is_owner()
    async def module(self, ctx, action: str = None, module: str = None) -> any:
        if action is None:
            return await ctx.send(embed = self.core.error("No module action provided."))

        elif module is None:
            return await ctx.send(embed = self.core.error(f"No module specified to {action}."))

        # Handle no module
        module = self.core.locate_module(module)
        if module is None:
            return await ctx.send(embed = self.core.error("Failed to locate specified module."))

        # Handle action
        tid = timer.start()
        result = {"unload": self.unload_module, "load": self.load_module}[action](module) if action in ["unload", "load"] else None
        if action == "reload":
            self.unload_module(module)
            result = self.load_module(module, reloaded = True)

        # Handle multiple command states
        embed = self.core.embed(description = f"```py\n{result}\n```")
        embed.set_author(name = "Module Handler", icon_url = self.bot.user.avatar_url)
        embed.set_footer(text = f"Completed in {timer.end(tid)} second(s).")
        return await ctx.send(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Module(bot))
