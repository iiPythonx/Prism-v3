# Copyright 2021-xx iiPython

# Modules
import ast
import discord
from discord.ext import commands
from discord.commands import Option

# Command class
class Eval(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core
        self.hidden = True

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

    @commands.slash_command(name = "eval", description = "Evaluate Python code.")
    @commands.is_owner()
    async def _eval(self, ctx, *, cmd: Option(str, "The code to evaluate.")) -> any:
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
                return await ctx.respond(embed = self._eval_(result, start))

            except discord.HTTPException:
                return await ctx.respond(embed = self.core.error("Output is too large to send."))

        except Exception as e:
            try:
                return await ctx.respond(embed = self._eval_(e, start))

            except discord.HTTPException:
                return await ctx.respond(embed = self.core.error("Output is too large to send."))

# Link
def setup(bot) -> None:
    return bot.add_cog(Eval(bot))
