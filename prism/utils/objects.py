# Copyright 2021 iiPython

# Modules
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
            items[item["name"]] = item["name"]

        return items

    def _dump_items(self):
        for item in self.items:
            if not inventory_db.test_for([("name", item), ("userid", self.owner_id)]):
                # create it
                inventory_db.create((self.owner_id, item, self.items[item]))

            else:
                # update it
                inventory_db.update({}, ())
                # print("need to update item: " + item)

        inventory_db.save()

    def add_item(self, name: str, amount: int = 1) -> None:
        if name in self.items:
            self.items[name] += amount

        else:
            self.items[name] = amount

        self._dump_items()

# Mapping
map = {
    "inv": Inventory
}
