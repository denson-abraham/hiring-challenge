import time

class TokenBucket:
    def __init__(self, limit, interval):
        self.limit = limit
        self.interval = float(interval)
        self.tokens = limit
        self.last_refill_time = time.time()

    def allow_request(self):
        current_time = time.time()
        time_diff = current_time - self.last_refill_time

        new_tokens = int(time_diff / self.interval)  # how many intervals have passed
        if new_tokens > 0:
            self.tokens = min(self.limit, self.tokens + new_tokens)
            self.last_refill_time += new_tokens * self.interval

        if self.tokens > 0:
            self.tokens -= 1
            return True
        return False

