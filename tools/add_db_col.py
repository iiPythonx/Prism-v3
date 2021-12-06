# Copyright 2021-xx iiPython
# tools/add_db_col.py
# Adds a column to an sqlite db, without requiring a reset

# Modules
import os
import json
import sqlite3
from rich import print
from prism.config import config

# Check the db folder
print("[yellow]Initializing databases...")
db_dir = config.get(["paths", "db_dir"])
if not os.path.isdir(db_dir):
    os.mkdir(db_dir)

# Create the databases
def create_db(name):
    conn = sqlite3.connect(os.path.abspath(os.path.join(db_dir, name + ".db")))
    cursor = conn.cursor()
    return conn, cursor

dbn = input("DB Name >> ")
name = input("Column Name >> ")
value = json.loads(input("Value (JSON syntax) >> "))
vtype = input("Value Type >> ")

c, cs = create_db(dbn)
cs.execute(f"ALTER TABLE {dbn} ADD COLUMN '{name}' '{vtype}'")
c.execute(f"UPDATE {dbn} SET {name}=?", (value,))

c.commit()
c.close()

# Finish process
print("[green]Column added.")
