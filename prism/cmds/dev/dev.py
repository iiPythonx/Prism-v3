# Copyright 2021 iiPython

# Modules
import os
import sys
import ast
import asyncio
import discord
import traceback
from discord.ext import commands
from discord.commands import Option

# Command class
class Dev(commands.Cog):
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

    def insert_returns(self, body) -> None:
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])

        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)

        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)

    def _eval_(self, output: str = None, timer_tid: str = "") -> discord.Embed:
        if not output:
            output = "[no output]"

        # Handle embed
        embed = self.core.embed(description = f"```py\n{output}\n```")
        embed.set_footer(text = f"Completed in {self.core.timer.end(timer_tid)} second(s).")
        return embed

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

    @commands.slash_command(name = "eval", description = "Evaluate Python code.")
    @commands.is_owner()
    async def _eval(self, ctx, *, cmd: Option(str, "The code to evaluate.")) -> any:
        await ctx.delete()
        env = {
            "ctx": ctx,
            "bot": self.bot,
            "core": self.core,
            "discord": discord,
            "commands": commands
        }
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        body = f"async def {fn_name}():\n{cmd}"
        start = self.core.timer.start()
        try:
            parsed = ast.parse(body)
            body = parsed.body[0].body

            self.insert_returns(body)

            exec(compile(parsed, filename = "<ast>", mode = "exec"), env)
            result = (await eval(f"{fn_name}()", env))

            try:
                return await ctx.send(embed = self._eval_(result, start))

            except discord.HTTPException:
                return await ctx.send(embed = self.core.error("Output is too large to send."))

        except Exception as e:
            try:
                return await ctx.send(embed = self._eval_(e, start))

            except discord.HTTPException:
                return await ctx.send(embed = self.core.error("Output is too large to send."))

    @commands.slash_command(description = "Handle Prism command modules.")
    @commands.is_owner()
    async def module(self, ctx, action: Option(str, "The action to perform", choices = ["reload", "load", "unload"]), module: Option(str, "The module path")) -> any:  # noqa
        module = self.core.locate_module(module)
        if module is None:
            return await ctx.respond(embed = self.core.error("Failed to locate specified module."))

        # Handle action
        tid = self.core.timer.start()
        result = {"unload": self.unload_module, "load": self.load_module}[action](module) if action in ["unload", "load"] else None
        if action == "reload":
            self.unload_module(module)
            result = self.load_module(module, reloaded = True)

        # Handle multiple command states
        embed = self.core.embed(description = f"```py\n{result}\n```")
        embed.set_author(name = "Module Handler", icon_url = self.bot.user.avatar.url)
        embed.set_footer(text = f"Completed in {self.core.timer.end(tid)} second(s).")
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Dev(bot))
