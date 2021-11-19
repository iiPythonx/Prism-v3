# Copyright 2021 iiPython

# Modules
import csv
from typing import Union
from discord.ext import commands
from discord.commands import Option

# Element handler
class ElementHandler(object):
    def __init__(self, csv_lines: list) -> None:
        self.elements = self._parse(csv_lines)

    def _parse(self, lines: list) -> list:
        elements, attrs = [], lines[0]
        for line in lines[1:]:
            elem = {}
            for attr in attrs:
                elem[attr] = line[attrs.index(attr)]

            elements.append(elem)

        return elements

    def find_element(self, query: str) -> Union[dict, None]:
        query = str(query).lower()
        for elem in self.elements:
            if query in [elem["AtomicNumber"], elem["Element"].lower(), elem["Symbol"].lower()]:
                return elem

        return None

# Command class
class Element(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.core = bot.core

        # Load element data
        self.data = self.core.generate_data_dir(__file__)
        with open(self.data.path("elements.csv"), newline = "") as csvfile:
            self.elements = ElementHandler(list(csv.reader(csvfile, delimiter = ",")))

    @commands.slash_command(description = "Gives you information about an element")
    async def element(self, ctx, element: Option(str, "The element to look up (name, symbol, atomic number)")) -> any:
        element = self.elements.find_element(element)
        if element is None:
            return await ctx.respond(embed = self.core.error("Failed to locate that element."))

        # Construct embed
        embed = self.core.embed(title = element["Element"], footer = ctx)
        embed.add_field(name = "Atomic Number", value = element["AtomicNumber"])
        embed.add_field(name = "Symbol", value = element["Symbol"])
        embed.add_field(name = "State", value = element["Phase"] or "N/A")
        embed.add_field(name = "Melting Point", value = f"{element['MeltingPoint']}°K")
        embed.add_field(name = "Boiling Point", value = f"{element['BoilingPoint']}°K")
        embed.add_field(name = "Discovered in", value = element["Year"] or "Unknown")
        embed.add_field(name = "Radioactive", value = {True: "yes", False: "no"}[element["Radioactive"] != ""])
        embed.add_field(name = "Discoverer", value = element["Discoverer"] or "Unknown")
        return await ctx.respond(embed = embed)

# Link
def setup(bot) -> None:
    return bot.add_cog(Element(bot))
