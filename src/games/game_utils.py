from enum import Enum


class GenericGameStateEnum(Enum):
    undefined = -1
    running = 0
    won = 1
    lost = 2


class Timer:
    def __init__(self, clb, fire_time, should_repeat=True):
        self.clb = clb
        self.elapsed = 0
        self.fire_time = fire_time
        self.should_repeat = should_repeat

    def trigger(self):
        self.clb()
        self.elapsed = 0
        if not self.should_repeat:
            self.clb = None

    def add_time(self, time):
        self.elapsed += time

    def fetch_time(self):
        return self.elapsed

    def fetch_remaining_time(self):
        return self.fire_time - self.elapsed

    def update(self, delta):
        if self.clb is None:
            return
        self.elapsed += delta
        if self.elapsed >= self.fire_time:
            self.trigger()
