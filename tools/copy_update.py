# Copyright 2021-xx iiPython

# Modules
import os

# Initialization
old_str = input("Former copyright notice: ")
new_str = input("New copyright string: ")

# Walker
for d, __, files in os.walk("./"):
    for f in files:
        if not f.endswith(".py"):
            continue

        path = os.path.join(d, f)
        with open(path, "r") as file:
            data = file.read()

        with open(path, "w") as file:
            file.write(data.replace(f"# {old_str}", f"# {new_str}"))
