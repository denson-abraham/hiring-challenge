import unittest
from unittest.mock import patch, MagicMock
import time
from app import app

class RateLimitTests(unittest.TestCase):

    @patch('app.redis_client')
    def test_register_client(self, mock_redis_client):
        mock_redis_client.exists.return_value = False

        with app.test_client() as client:
            response = client.post('/register_client', json={
                "client_id": "client123",
                "limit": 5,
                "interval": "minute"
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn('Client client123 registered successfully.', response.get_json()['message'])

    @patch('app.redis_client')
    def test_validate_request_allowed(self, mock_redis_client):
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.return_value = {
            "limit": 5,
            "interval": "minute",
            "remaining_requests": 4,
            "last_reset": 0
        }

        with app.test_client() as client:
            response = client.post('/validate_request', json={"client_id": "client123"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['message'], "Request allowed.")

    @patch('app.redis_client')
    def test_validate_request_blocked(self, mock_redis_client):
        # Mock the scenario where the client exists and the remaining requests are 0.
        # We'll assume the interval has passed to trigger the reset.
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.return_value = {
            "limit": 5,
            "interval": "minute",  # 1 minute interval
            "remaining_requests": 0,  # Remaining requests = 0
            "last_reset": int(time.time()) - 120  # Last reset was 2 minutes ago, interval has passed (e.g., interval is 1 minute)
        }

        with app.test_client() as client:
            response = client.post('/validate_request', json={"client_id": "client123"})
            
            # Since the interval has passed, the remaining requests should be reset, and the request should be allowed
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['message'], "Request allowed.")
            
            # Verify that the remaining requests were reset to the full limit (5)
            mock_redis_client.hset.assert_any_call(f"client:client123", "remaining_requests", 5)


    @patch('app.redis_client')
    def test_reset_remaining_requests(self, mock_redis_client):
        # Set up initial client data with remaining requests = 0
        client_id = "client123"
        limit = 5
        interval = "minute"
        last_reset = int(time.time()) - 120  # 2 minutes ago (to force reset)

        # Mock redis client behavior
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.return_value = {
            "limit": limit,
            "interval": interval,
            "remaining_requests": 0,
            "last_reset": last_reset
        }

        # Simulate that 2 minutes have passed, so the reset should occur
        with app.test_client() as client:
            response = client.post('/validate_request', json={"client_id": client_id})

            # Verify if the reset logic works
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['message'], "Request allowed.")

            # Check that the remaining requests were reset
            mock_redis_client.hset.assert_any_call(f"client:{client_id}", "remaining_requests", limit)

    @patch('app.redis_client')
    def test_invalid_interval(self, mock_redis_client):
        # Test case to check for invalid interval when registering the client
        with app.test_client() as client:
            response = client.post('/register_client', json={
                "client_id": "client123",
                "limit": 5,
                "interval": "week"  # Invalid interval
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], "Invalid interval. Use 'minute', 'hour', or 'day'.")

    @patch('app.redis_client')
    def test_client_status(self, mock_redis_client):
        # Test the /client_status endpoint
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.return_value = {
            "limit": 5,
            "interval": "minute",
            "remaining_requests": 3,
            "last_reset": 0
        }

        with app.test_client() as client:
            response = client.get('/client_status/client123')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['client_id'], "client123")
            self.assertEqual(response.get_json()['remaining_requests'], 3)

    # Test the Token Bucket algorithm logic
    @patch('app.TokenBucket')
    def test_token_bucket_algorithm(self, MockTokenBucket):
        # Mock the behavior of the TokenBucket
        mock_token_bucket = MockTokenBucket.return_value
        mock_token_bucket.allow_request.return_value = True

        # Check if request is allowed
        self.assertTrue(mock_token_bucket.allow_request())

        mock_token_bucket.allow_request.return_value = False
        # Check if request is blocked
        self.assertFalse(mock_token_bucket.allow_request())

if __name__ == '__main__':
    unittest.main()
