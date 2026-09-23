import time


class Timer:
    def __init__(self, label: str) -> None:
        self.label = label

    def __enter__(self):
        self.start = time.monotonic()

    def __exit__(self, exc_type, exc_val, exc_tb):
        now = time.monotonic()
        elapsed = (now - self.start) * 1000
        print(self.label + ": " + format(elapsed, ".1f") + " ms")
