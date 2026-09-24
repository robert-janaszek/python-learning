import time
from types import TracebackType


class Timer:
    def __init__(self, label: str) -> None:
        self.label = label

    def __enter__(self) -> None:
        self.start = time.monotonic()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        now = time.monotonic()
        elapsed = (now - self.start) * 1000
        print(self.label + ": " + format(elapsed, ".1f") + " ms")
