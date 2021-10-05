# Copyright 2021 iiPython

# Modules
import os
import sys
import ast
import asyncio
import traceback
from discord.ext import commands
from prism.utils.timer import timer

# Command class
class Module(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.hidden = True

        # Handle autoreloading
        if "--debug" in sys.argv:
            if "autoreload" not in self.bot.core.storage:
                self.bot.core.storage["autoreload"] = True
                self.bot.loop.create_task(self.autoreload())

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
        embed.set_author(name = "Module Handler", icon_url = self.bot.user.avatar.url)
        embed.set_footer(text = f"Completed in {timer.end(tid)} second(s).")
        return await ctx.send(embed = embed)

    # Autoreload handler
    async def autoreload(self):
        command_dir = self.bot.core.storage["cmd_path"]
        commands = []
        for cat in os.listdir(command_dir):
            if cat[0] == "_":
                continue

            commands += [os.path.join(command_dir, cat, file) for file in os.listdir(os.path.join(command_dir, cat)) if not file[0] == "_"]

        # Handle initialization
        def ch_count(path):
            total = 0
            with open(path, encoding = "UTF-8") as file:
                for line in file:
                    total += len(line)

            return total

        if not hasattr(self, "autoreload_cache"):
            self.autoreload_cache = {}

        # Handle autoreload
        self.bot.log("info", "Debugging reloader started.")
        for command in commands:
            self.autoreload_cache[command] = ch_count(command)

        await self.bot.wait_until_ready()
        while not self.bot.is_closed():

            # Check for a file change
            for command in commands:
                chars = ch_count(command)
                if chars != self.autoreload_cache[command]:
                    self.autoreload_cache[command] = chars

                    # Check if file is valid to reload
                    try:
                        with open(command, "r", encoding = "utf8") as f:
                            ast.parse(f.read())

                        # Reload extension
                        self.unload_module(command.replace(".py", "").replace("/", "."))
                        self.load_module(command.replace(".py", "").replace("/", "."))

                        self.bot.log("success", f"Reloaded {command}")

                    except Exception:
                        pass

            await asyncio.sleep(1)

# Link
def setup(bot) -> None:
    return bot.add_cog(Module(bot))
