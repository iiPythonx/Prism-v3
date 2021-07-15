# Copyright 2021 iiPython

# Modules
from typing import Union
from datetime import datetime
from secrets import token_hex

# Timer class
class Timer(object):
    def __init__(self) -> None:
        self._st_times = {}
        self._ret_keys = {"s": lambda x: x, "ms": lambda x: float(x) * 1000}

    def start(self) -> str:
        timer_id = token_hex(26)
        self._st_times[timer_id] = datetime.now()
        return timer_id

    def end(self, timer_id: str, return_as: str = "s", as_int: bool = False) -> Union[str, int]:
        if timer_id not in self._st_times:
            raise RuntimeError("invalid timer id: '{}'".format(timer_id))

        st_time = self._st_times[timer_id]
        del self._st_times[timer_id]

        # Handle return value
        secs = round((datetime.now() - st_time).total_seconds(), 2)
        vals = self._ret_keys[return_as](secs)

        return str(vals) if not as_int else int(round(vals))

# Initialization
timer = Timer()
