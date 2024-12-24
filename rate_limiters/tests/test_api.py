import unittest
from unittest.mock import patch
from app import app
import time

class RateLimitApiTests(unittest.TestCase):
    
    @patch('app.redis_client')
    def test_register_client(self, mock_redis_client):
        # Mock Redis behavior when registering a client
        mock_redis_client.exists.return_value = False
        mock_redis_client.hset.return_value = True
        
        current_timestamp = int(time.time())
        with app.test_client() as client:
            response = client.post('/register_client', json={
                "client_id": "client123",
                "limit": 5,
                "interval": "minute"
            })
            
            # Assert the status code and response message
            self.assertEqual(response.status_code, 200)
            self.assertIn('Client client123 registered successfully.', response.get_json()['message'])
            
            # Get the current timestamp to check against last_reset
            #current_timestamp = int(time.time())
            
            # Verify Redis interaction - check if hset was called with the expected data
            mock_redis_client.hset.assert_any_call(
                "client:client123", 
                mapping={
                    "limit": 5,
                    "interval": "minute",
                    "remaining_requests": 5,
                    "last_reset": current_timestamp  # Use the current timestamp in the test
                }
            )

    @patch('app.redis_client')
    def test_validate_request_allowed(self, mock_redis_client):
        # Mock Redis behavior for validating request
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.return_value = {
            "limit": 5,
            "interval": "minute",
            "remaining_requests": 4,
            "last_reset": 0  # Initial value for last reset
        }
        
        with app.test_client() as client:
            response = client.post('/validate_request', json={"client_id": "client123"})
            
            # Assert that the request is allowed and remaining requests are decremented
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['message'], "Request allowed.")
            
            # Verify Redis interaction - remaining_requests should be decremented by 1
            mock_redis_client.hincrby.assert_called_with("client:client123", "remaining_requests", -1)

    @patch('app.redis_client')
    def test_validate_request_blocked(self, mock_redis_client):
        # Mock Redis behavior where remaining requests are 0
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.return_value = {
            "limit": 5,
            "interval": "minute",
            "remaining_requests": 0,
            "last_reset": 0  # Reset timestamp
        }

        with app.test_client() as client:
            # Simulate that the 5th request has been made (remaining_requests = 0)
            response = client.post('/validate_request', json={"client_id": "client123"})
            
            # Assert that the request is allowed (200 status code)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['message'], "Request allowed.")

            # Update mock data to reflect that no remaining requests are left
            mock_redis_client.hgetall.return_value = {
                "limit": 5,
                "interval": "minute",
                "remaining_requests": 0,
                "last_reset": int(time.time())  # Adjust as needed based on the current time
            }
            
            # Simulate the next request, now remaining_requests should be 0
            response = client.post('/validate_request', json={"client_id": "client123"})

            # Assert that the request is blocked because no remaining requests are available
            self.assertEqual(response.status_code, 429)
            self.assertEqual(response.get_json()['message'], "Too Many Requests")
            
            # Verify no change in remaining requests for this blocked request
            mock_redis_client.hincrby.assert_not_called()

    @patch('app.redis_client')
    def test_register_client_invalid_client_id(self, mock_redis_client):
        with app.test_client() as client:
            # Test client_id is None
            response = client.post('/register_client', json={
                "client_id": None,
                "limit": 5,
                "interval": "minute"
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], "Missing or invalid client_id. It must be a non-empty string.")
            
            # Test client_id is empty string
            response = client.post('/register_client', json={
                "client_id": "",
                "limit": 5,
                "interval": "minute"
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], "Missing or invalid client_id. It must be a non-empty string.")
            
            # Test client_id is not a string
            response = client.post('/register_client', json={
                "client_id": 123,
                "limit": 5,
                "interval": "minute"
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], "Missing or invalid client_id. It must be a non-empty string.")
    
    @patch('app.redis_client')
    def test_register_client_client_exists(self, mock_redis_client):
        with app.test_client() as client:
            # Simulate a new client registration
            mock_redis_client.exists.return_value = False  # No client exists initially
            response = client.post('/register_client', json={
                "client_id": "client123",
                "limit": 5,
                "interval": "minute"
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['message'], "Client client123 registered successfully.")

            # Now simulate that the client already exists in Redis
            mock_redis_client.exists.return_value = True  # The client already exists
            response = client.post('/register_client', json={
                "client_id": "client123",
                "limit": 5,
                "interval": "minute"
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], "Client client123 already exists.")

    @patch('app.redis_client')
    def test_register_client_invalid_limit(self, mock_redis_client):
        with app.test_client() as client:
            # Test limit is None
            response = client.post('/register_client', json={
                "client_id": "client123",
                "limit": None,
                "interval": "minute"
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], "Missing or invalid limit. It must be a positive integer.")
            
            # Test limit is not an integer
            response = client.post('/register_client', json={
                "client_id": "client123",
                "limit": "five",
                "interval": "minute"
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], "Missing or invalid limit. It must be a positive integer.")
            
            # Test limit is negative
            response = client.post('/register_client', json={
                "client_id": "client123",
                "limit": -5,
                "interval": "minute"
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], "Missing or invalid limit. It must be a positive integer.")

    @patch('app.redis_client')
    def test_register_client_invalid_interval(self, mock_redis_client):
        # Test case for invalid interval
        with app.test_client() as client:
            response = client.post('/register_client', json={
                "client_id": "client123",
                "limit": 5,
                "interval": "week"  # Invalid interval
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], "Invalid interval. Use 'minute', 'hour', or 'day'.")

    @patch('app.redis_client')
    def test_validate_request_reset_remaining(self, mock_redis_client):
        # Mock Redis behavior for resetting remaining requests when the interval has passed
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.return_value = {
            "limit": 5,
            "interval": "minute",
            "remaining_requests": 0,
            "last_reset": 0  # Assume last reset was long ago, so interval should have passed
        }
        
        with app.test_client() as client:
            response = client.post('/validate_request', json={"client_id": "client123"})
            
            # Assert that the request is allowed after the reset (remaining requests should be reset)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['message'], "Request allowed.")
            
            # Verify Redis interaction - the remaining requests should be reset to the limit (5)
            mock_redis_client.hset.assert_any_call("client:client123", "remaining_requests", 5)

    @patch('app.redis_client')
    def test_client_status(self, mock_redis_client):
        # Mock Redis behavior for fetching client status
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.return_value = {
            "limit": 5,
            "interval": "minute",
            "remaining_requests": 3,
            "last_reset": 0
        }
        
        with app.test_client() as client:
            response = client.get('/client_status/client123')
            
            # Assert that the client status is correctly returned
            self.assertEqual(response.status_code, 200)
            client_data = response.get_json()
            self.assertEqual(client_data['client_id'], 'client123')
            self.assertEqual(client_data['remaining_requests'], 3)
            self.assertEqual(client_data['limit'], 5)
            self.assertEqual(client_data['interval'], 'minute')
            
            # Verify Redis interaction - ensure we fetched the correct data
            mock_redis_client.hgetall.assert_called_with("client:client123")

if __name__ == '__main__':
    unittest.main()
