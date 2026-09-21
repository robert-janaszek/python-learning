from collections import defaultdict
import time


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.hits = defaultdict[str, list[float]](list)

    def __call__(self, user_id: str) -> bool:
        now = time.monotonic()
        user_hits = self.hits[user_id]
        non_expired = [hit for hit in user_hits if hit > now - self.window_seconds]

        if len(non_expired) >= self.max_requests:
            self.hits[user_id] = non_expired
            return False
        
        non_expired.append(now)
        self.hits[user_id] = non_expired

        return True

    def __repr__(self) -> str:
        return "RateLimiter(max_requests=" + str(self.max_requests) + ", window=" + str(self.window_seconds) + ")"
