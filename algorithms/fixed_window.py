import time

class FixedWindowCounter:
    def __init__(self, limit, interval):
        self.limit = int(limit)
        self.interval = float(interval)
        self.request_count = 0
        self.window_start_time = time.time()

    def allow_request(self):
        current_time = time.time()

        # Reset the counter if the window has elapsed
        if current_time - self.window_start_time >= self.interval:
            self.request_count = 0
            self.window_start_time = current_time

        if self.request_count < self.limit:
            self.request_count += 1
            return True
        return False

