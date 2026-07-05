from time import time

class TimeObject:
    def __init__(self, duration: int):
        self.start = time()
        self.duration = duration

    def count_time(self) -> int:
        current_time = time() 
        return int(current_time - self.start)

    def is_elapsed(self) -> bool:
        current_time = time()
        if self.start + self.duration - current_time <= 0:
            return True
        else:
            return False