# Copyright 2021 iiPython

# Modules
from .images import Images
from ..database import Database

# Load databases
database = Database()
inventory_db = database.load_db("inventory")

# Inventory class
class Inventory(object):
    def __init__(self, owner_id: int) -> None:
        self.owner_id = owner_id
        self.items = self._load_inv()

    def _load_inv(self) -> list:
        data = inventory_db.getall(("userid", self.owner_id))
        if data is None:
            return {}

        items = {}
        for item in data:
            items[item["name"]] = item["amount"]

        return items

    def add_item(self, name: str, amount: int = 1) -> None:
        if name in self.items:
            self.items[name] += amount
            inventory_db.update({"amount": self.items[name]}, [("userid", self.owner_id), ("name", name)])

        else:
            self.items[name] = amount
            inventory_db.create((self.owner_id, name, amount))

        inventory_db.save()

# Mapping
map = {
    "inv": Inventory,
    "img": Images()
}
