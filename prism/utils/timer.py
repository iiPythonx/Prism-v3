# Copyright 2021 iiPython

# Modules
from datetime import datetime

# Timer class
class Timer(object):
    def __init__(self) -> None:
        self._st_times = {}

    def start(self, timer_name: str) -> None:
        if timer_name in self._st_times:
            raise RuntimeError("a timer with the name '{}' is already running".format(timer_name))

        self._st_times[timer_name] = datetime.now()

    def end(self, timer_name: str) -> str:
        if timer_name not in self._st_times:
            raise RuntimeError("no such timer: '{}'".format(timer_name))

        st_time = self._st_times[timer_name]
        del self._st_times[timer_name]

        return str(round((datetime.now() - st_time).total_seconds(), 2))

# Initialization
timer = Timer()
