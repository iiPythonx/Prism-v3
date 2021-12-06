# Copyright 2021-xx iiPython

# Modules
import discord
from discord.ext import commands
from discord.commands import Option
from prism.core.models import Paginator

# Shop pageinator class
class ShopPagination(Paginator):
    def create_page(self, page: int) -> discord.Embed:
        embed = self.core.embed(title = "Prism Shop")
        for item in self.pages[page]:
            embed.add_field(
                name = f":{item['emoji']}:  **{item['name']}** — __{self.core.format_coins(item['price'])} coins__",
                value = item["body"],
                inline = False
            )

        embed.set_footer(text = f"Prism Shop | Page {page + 1} of {len(self.pages)}")
        return embed

# Command class
class Shop(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        self.items = [
            {"name": "Cheese Slice", "emoji": "cheese", "price": 5000, "body": "It's cheese, what do you expect?"},
            {"name": "Hotdog", "emoji": "hotdog", "price": 5000, "body": "Bad day? Have a hotdog."},
            {"name": "Bank Note", "emoji": "scroll", "price": 125000, "body": "Allows you to sell items for full price.", "stack": 1}
        ]
        self.sellable_items = {i["name"]: i["price"] for i in self.items}
        self.items = list(self.chunk_items(self.items))

    def chunk_items(self, items: list) -> list:
        for i in range(0, len(items), 5):
            yield items[i:i + 5]

    @commands.slash_command(description = "Check out the Prism item shop.")
    async def shop(self, ctx, page: Option(int, "The page to view", required = False, default = 1)) -> any:
        try:
            paginator = ShopPagination(ctx, self.items, page)
            return await ctx.respond(embed = paginator.create_page(paginator.current_page), view = paginator)

        except ValueError:
            return await ctx.respond(embed = self.core.error("Invalid page number."))

    @commands.slash_command(description = "Purchase an item from the shop.")
    async def buy(self, ctx, item: Option(str, "The name of the item to purchase (any form)"), amount: Option(int, "The amount to buy", required = False, default = 1)) -> any:
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author))

        # Attempt to find item
        raw_item = None
        for page in self.items:
            for _item in page:
                if _item["name"].lower().replace(" ", "") == item.lower().replace(" ", ""):
                    raw_item = _item
                    break

        if raw_item is None:
            return await ctx.respond(embed = self.core.error("No item with that name was found."))

        item = raw_item
        item_name = f"{amount} {item['name']}s" if amount > 1 else f"a {item['name']}"

        # Handle price checking
        bal = db.get(("userid", ctx.author.id), "balance")
        if bal < (item["price"] * amount):
            return await ctx.respond(embed = self.core.error(f"You need {self.core.format_coins((item['price'] * amount) - bal)} more coins to buy {item_name}."))

        # Handle stacking
        max_stack = item.get("stack", 100)
        user_inv = self.core.inventory(ctx.author.id)
        if user_inv.items.get(item["name"], 0) == max_stack:
            return await ctx.respond(embed = self.core.error(f"You have reached the stack limit for that item ({max_stack})."))

        elif user_inv.items.get(item["name"], 0) + amount > max_stack:
            return await ctx.respond(embed = self.core.error(f"Purchasing {item_name} will go over the stack limit ({max_stack}), chill out."))

        # Update balance + inventory
        db.update({"balance": bal - (item["price"] * amount)}, ("userid", ctx.author.id))
        user_inv.add_item(item["name"], amount)
        return await ctx.respond(embed = self.core.small_embed(f"You have successfully bought {item_name}."))

    @commands.slash_command(description = "Sell an item from your inventory.")
    async def sell(self, ctx, item: Option(str, "The item to sell (any form)"), amount: Option(int, "The amount to sell", required = False, default = 1)) -> any:
        db = self.bot.db.load_db("users")
        if not db.test_for(("userid", ctx.author.id)):
            return await ctx.respond(embed = self.core.noacc(ctx, ctx.author))

        # Attempt to find item
        raw_item, user_inv = None, self.core.inventory(ctx.author.id)
        for _item in user_inv.items:
            if _item.lower().replace(" ", "") == item.lower().replace(" ", ""):
                raw_item = {"name": _item, "amount": user_inv.items[_item]}
                break

        if raw_item is None:
            return await ctx.respond(embed = self.core.error("You don't have an item with that name."))

        elif raw_item["name"] not in self.sellable_items:
            return await ctx.respond(embed = self.core.error("That item is currently not sellable."))

        # Checks
        item_name = f"{amount} {raw_item['name']}s" if amount > 1 else f"1 {raw_item['name']}"
        if amount > raw_item["amount"]:
            return await ctx.respond(embed = self.core.error(f"You don't have {item_name}."))

        # Sell item
        user_inv.remove_item(raw_item["name"], amount)
        sell_price = self.sellable_items[raw_item["name"]] * amount
        if "Bank Note" not in user_inv.items:
            sell_price /= 2

        db.update({"balance": db.get(("userid", ctx.author.id), "balance") + sell_price}, ("userid", ctx.author.id))
        return await ctx.respond(
            embed = self.core.embed(
                title = f"Sold {item_name}!",
                description = f"You have gained {self.core.format_coins(sell_price)} coins.",
                footer = ctx
            )
        )

# Link
def setup(bot) -> None:
    return bot.add_cog(Shop(bot))
