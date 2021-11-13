# Copyright 2021 iiPython
# Helper functions for bank management

# Modules
from prism.database import Database, DBConnection

# Initialization
_bank_max_val = 9223372036854775807
db = Database().load_db("bank")

# Helper functions
def init_user(user_id: int) -> None:
    if db.test_for(("userid", user_id)):
        return

    db.create((user_id, 0))

def get_bank_balance(user_id: int) -> int:
    init_user(user_id)
    return db.get(("userid", user_id), "balance")

def can_deposit(user_id: int, amount: int) -> bool:
    bal = get_bank_balance(user_id)
    if bal + amount > _bank_max_val:
        return False

    return True

def bank_deposit(user_id: int, amount: int, udb: DBConnection) -> None:
    if not isinstance(udb, DBConnection):
        raise RuntimeError("passed database is not a valid DBConnection!")

    db.update({"balance": get_bank_balance(user_id) + amount}, ("userid", user_id))
    udb.update({"balance": udb.get(("userid", user_id), "balance") - amount}, ("userid", user_id))

def bank_withdraw(user_id: int, amount: int, udb: DBConnection) -> None:
    if not isinstance(udb, DBConnection):
        raise RuntimeError("passed database is not a valid DBConnection!")

    db.update({"balance": get_bank_balance(user_id) - amount}, ("userid", user_id))
    udb.update({"balance": udb.get(("userid", user_id), "balance") + amount}, ("userid", user_id))
