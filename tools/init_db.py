# Copyright 2021 iiPython
# tools/init_db.py
# Initializes the required database files

# Modules
import os
import sqlite3
from rich import print

# Check the db folder
print("[yellow]Initializing databases...")
if not os.path.isdir("db"):
    os.mkdir("db")

# Create the databases
def create_db(name):
    conn = sqlite3.connect(os.path.abspath(os.path.join("db", name + ".db")))
    cursor = conn.cursor()
    return conn, cursor

c, cs = create_db("users")
cs.execute("""
CREATE TABLE IF NOT EXISTS users (
    userid integer,
    balance long
)
""")
c.commit()
c.close()

# Finish process
print("  [green]databases initialized.")
