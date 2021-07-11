# Copyright 2021 iiPython
# tools/init_db.py
# Initializes the required database files

# Modules
import os
import sqlite3
from rich import print
from prism.config import config

# Check the db folder
print("[yellow]Initializing databases...")
db_dir = config.get("db_dir")

if not os.path.isdir(db_dir):
    os.mkdir(db_dir)

# Create the databases
def create_db(name):
    conn = sqlite3.connect(os.path.abspath(os.path.join(db_dir, name + ".db")))
    cursor = conn.cursor()
    return conn, cursor

c, cs = create_db("users")
cs.execute("""
CREATE TABLE IF NOT EXISTS users (
    userid integer,
    balance long,
    bio text
)
""")
c.commit()
c.close()

c, cs = create_db("inventory")
cs.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    userid integer,
    name text,
    amount integer
)
""")
c.commit()
c.close()

# Finish process
print("  [green]databases initialized.")
