import time

class TokenBucket:
    def __init__(self, window_size, max_requests):
        self.window_size = window_size  # Time period for token refill (in seconds)
        self.max_requests = max_requests  # Max tokens available
        self.tokens = max_requests  # Start with max tokens
        self.last_refill_time = time.time()

    def refill_tokens(self):
        now = time.time()
        time_elapsed = now - self.last_refill_time  # Calculate the elapsed time since the last refill

        if time_elapsed >= self.window_size:  # Refill only if the window size has passed
            # Tokens to add is proportional to the elapsed time
            tokens_to_add = int(time_elapsed // self.window_size * self.max_requests)
            self.tokens = min(self.max_requests, self.tokens + tokens_to_add)  # Cap at max_requests
            self.last_refill_time = now  # Reset the last refill time to now

    def allow_request(self):
        self.refill_tokens()  # Ensure tokens are refilled before processing the request

        if self.tokens > 0:
            self.tokens -= 1  # Deduct a token for the request
            return True
        else:
            return False
