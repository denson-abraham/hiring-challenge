import time

def validate_fixed_window(redis_client, client_id, limit, interval):
    client_key = f"client:{client_id}"
    interval_seconds = 60 if interval == "minute" else 3600  # 1 minute = 60 seconds, 1 hour = 3600 seconds
    
    # Get the current window based on the interval
    current_window = int(time.time()) // interval_seconds
    
    # Use a unique key for the current window to track requests
    window_key = f"{client_key}:window:{current_window}"
    
    # Get the current request count in the window
    current_count = redis_client.get(window_key)

    # If this is the first request in the window, set it with expiration time
    if not current_count:
        redis_client.set(window_key, 0, ex=interval_seconds)

    # Increment the request count for the current window
    current_count = int(redis_client.incr(window_key))

    # Check if the current request count exceeds the limit
    if current_count > limit:
        return False  # Too many requests in this window
    
    # Allow request if under the limit
    return True
