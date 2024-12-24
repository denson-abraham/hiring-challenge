from flask import Flask, request, jsonify
import redis
from algorithms.token_bucket import TokenBucket
from algorithms.fixed_window import validate_fixed_window
import time

app = Flask(__name__)

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def get_interval_seconds(interval):
    """Return the number of seconds for the given interval."""
    if interval == "minute":
        return 60  # 1 minute = 60 seconds
    elif interval == "hour":
        return 3600  # 1 hour = 3600 seconds
    elif interval == "day":
        return 86400  # 1 day = 86400 seconds
    else:
        return None  # Default to 1 minute if invalid interval is passed

@app.route('/register_client', methods=['POST'])
def register_client():
    data = request.get_json()
    client_id = data.get('client_id')
    limit = data.get('limit')
    interval = data.get('interval')

    if not client_id or not isinstance(client_id, str) or len(client_id) == 0:
        return jsonify({"error": "Missing or invalid client_id. It must be a non-empty string."}), 400

    if not limit or not isinstance(limit, int) or limit <= 0:
        return jsonify({"error": "Missing or invalid limit. It must be a positive integer."}), 400

    if not interval or get_interval_seconds(interval) is None:
        return jsonify({"error": "Invalid interval. Use 'minute', 'hour', or 'day'."}), 400
    
    # Check if the client already exists
    client_key = f"client:{client_id}"
    if redis_client.exists(client_key):
        return jsonify({"error": f"Client {client_id} already exists."}), 400

    redis_client.hset(client_key, mapping={
        "limit": limit,
        "interval": interval,
        "remaining_requests": limit,
        "last_reset": int(time.time())  # Store the last reset time
    })

    return jsonify({"message": f"Client {client_id} registered successfully."}), 200


@app.route('/validate_request', methods=['POST'])
def validate_request():
    data = request.get_json()
    client_id = data.get('client_id')

    if not client_id:
        return jsonify({"error": "client_id is required"}), 400

    client_key = f"client:{client_id}"

    if not redis_client.exists(client_key):
        return jsonify({"error": "Client not found"}), 404

    client_data = redis_client.hgetall(client_key)
    limit = int(client_data["limit"])
    interval = client_data["interval"]
    last_reset = int(client_data["last_reset"])

    # Get interval in seconds
    interval_seconds = get_interval_seconds(interval)

    # Calculate the time difference from the last reset
    current_time = int(time.time())
    time_difference = current_time - last_reset

    # If the interval time has passed, reset the remaining requests
    if time_difference >= interval_seconds:
        redis_client.hset(client_key, "remaining_requests", limit)
        redis_client.hset(client_key, "last_reset", current_time)
        # Reload the client data to get the updated remaining_requests
        client_data = redis_client.hgetall(client_key)

    remaining_requests = int(client_data["remaining_requests"])

    # If remaining_requests is 0, and the interval has passed, reset the count
    if remaining_requests == 0:
        # If the interval has passed, reset the remaining requests
        if time_difference >= interval_seconds:
            redis_client.hset(client_key, "remaining_requests", limit)
            redis_client.hset(client_key, "last_reset", current_time)
            remaining_requests = limit
            return jsonify({"message": "Request allowed."}), 200
        else:
            return jsonify({"message": "Too Many Requests"}), 429

    # If there are remaining requests, allow the request
    if remaining_requests > 0:
        redis_client.hincrby(client_key, "remaining_requests", -1)
        return jsonify({"message": "Request allowed."}), 200

    return jsonify({"message": "Too Many Requests"}), 429

    

@app.route('/client_status/<client_id>', methods=['GET'])
def client_status(client_id):
    client_key = f"client:{client_id}"

    if not redis_client.exists(client_key):
        return jsonify({"detail": "Client not found."}), 404

    client_data = redis_client.hgetall(client_key)
    remaining_requests = int(client_data["remaining_requests"])
    limit = int(client_data["limit"])
    interval = client_data["interval"]

    return jsonify({
        "client_id": client_id,
        "remaining_requests": remaining_requests,
        "limit": limit,
        "interval": interval
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
