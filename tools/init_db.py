# Copyright 2021-xx iiPython
# tools/init_db.py
# Initializes the required database files

# Modules
import os
import json
import sqlite3
from rich import print

# Check the db folder
with open("config.json", "r") as fh:
    config = json.loads(fh.read())

print("[yellow]Initializing databases...")
db_dir = config["paths"]["db_dir"]
if not os.path.isdir(db_dir):
    os.mkdir(db_dir)

# Create the databases
def create_db(name: str, cmd: str) -> None:
    conn = sqlite3.connect(os.path.abspath(os.path.join(db_dir, name + ".db")))
    cursor = conn.cursor()
    cursor.execute(cmd)
    conn.commit()
    conn.close()

create_db("users", """
CREATE TABLE IF NOT EXISTS users (
    userid integer,
    balance long,
    bio text,
    accent text
)
""")
create_db("inventory", """
CREATE TABLE IF NOT EXISTS inventory (
    userid integer,
    name text,
    amount integer
)
""")
create_db("guilds", """
CREATE TABLE IF NOT EXISTS guilds (
    id integer,
    prefix text
)
""")
create_db("bank", """
CREATE TABLE IF NOT EXISTS bank (
    userid integer,
    balance long
)
""")

# Finish process
print("  [green]databases initialized.")
