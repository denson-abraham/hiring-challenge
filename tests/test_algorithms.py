import time
from algorithms.token_bucket import TokenBucket
from algorithms.fixed_window import FixedWindowCounter

def test_token_bucket():
    token_bucket = TokenBucket(3, 1)  # Limit 3 tokens, 1 second interval

    # first 3 requests
    assert token_bucket.allow_request() is True
    assert token_bucket.allow_request() is True
    assert token_bucket.allow_request() is True

    # next request - fail
    assert token_bucket.allow_request() is False

    # refill the tokens
    time.sleep(1)
    assert token_bucket.allow_request() is True

def test_fixed_window():
    fixed_window = FixedWindowCounter(3, 5)  # Limit 3 requests, 5 seconds interval

    # 3 requests within the window
    assert fixed_window.allow_request() is True
    assert fixed_window.allow_request() is True
    assert fixed_window.allow_request() is True

    # new request within the same window - fail
    assert fixed_window.allow_request() is False

    # reset the window
    time.sleep(5)
    assert fixed_window.allow_request() is True

def test_zero_limit():
    token_bucket = TokenBucket(0, 1)
    fixed_window = FixedWindowCounter(0, 1)

    # Zero limits
    assert token_bucket.allow_request() is False
    assert fixed_window.allow_request() is False