from flask import Flask, request, jsonify
from algorithms.token_bucket import TokenBucket
from algorithms.fixed_window import FixedWindowCounter

app = Flask(__name__)

clients = {}


def parse_interval(interval):
    try:
        unit = interval[-1].lower()
        value = int(interval[:-1])
        if unit == 's':  # seconds
            return value
        elif unit == 'm':  # minutes
            return value * 60
        elif unit == 'h':  # hours
            return value * 3600
        else:
            raise ValueError
    except (ValueError, IndexError):
        raise ValueError("Invalid interval format. Use 's' for seconds, 'm' for minutes, 'h' for hours.")


@app.route('/register_client', methods=['POST'])
def register_client():
    data = request.get_json()

    # Extract client data
    client_id = data.get("client_id")
    limit = data.get("limit")
    interval = data.get("interval")
    algorithm = data.get("algorithm", "token_bucket").lower()  # Default to token_bucket

    # Check if all required fields are provided
    if not client_id or not limit or not interval:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        interval_in_seconds = parse_interval(interval)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Create rate-limiting algorithm object
    if algorithm == "token_bucket":
        algorithm_object = TokenBucket(limit, interval_in_seconds)
    elif algorithm == "fixed_window":
        algorithm_object = FixedWindowCounter(limit, interval_in_seconds)
    else:
        return jsonify({"error": "Invalid algorithm specified"}), 400

    # Store the client configuration
    clients[client_id] = {
        "algorithm": algorithm_object
    }

    return jsonify({"message": f"Client {client_id} registered successfully with {algorithm} algorithm"}), 201


@app.route('/validate_request', methods=['POST'])
def validate_request():
    data = request.get_json()
    client_id = data.get("client_id")

    # Check if the client exists
    if client_id not in clients:
        return jsonify({"error": "Client not found"}), 404

    # Get client's algorithm object
    client = clients[client_id]
    algorithm = client["algorithm"]

    # Check if the request is allowed based on the algorithm
    if algorithm.allow_request():
        return jsonify({"message": "Request allowed"}), 200
    else:
        return jsonify({"error": "Too many requests, rate limit exceeded"}), 429


@app.route('/client_status/<client_id>', methods=['GET'])
def client_status(client_id):
    # Check if the client exists
    if client_id not in clients:
        return jsonify({"error": "Client not found"}), 404

    # Get client's algorithm object
    client = clients[client_id]
    algorithm = client["algorithm"]

    # Return current status (remaining requests)
    if isinstance(algorithm, TokenBucket):
        remaining_requests = algorithm.tokens
    elif isinstance(algorithm, FixedWindowCounter):
        remaining_requests = algorithm.limit - algorithm.request_count

    return jsonify({
        "client_id": client_id,
        "remaining_requests": remaining_requests,
        "limit": algorithm.limit,
        "interval": algorithm.interval
    }), 200


if __name__ == '__main__':
    app.run(debug=True)


# from flask import Flask, request, jsonify
# from algorithms.token_bucket import TokenBucket
# from algorithms.fixed_window import FixedWindowCounter
#
# app = Flask(__name__)
#
# # In-memory storage for clients' rate-limiting configurations and request counts
# clients = {}
#
# '''
# {
#   "client_id": "client123",
#   "limit": 5,
#   "interval": "60",
#   "algorithm": "token_bucket"
# }
# '''
#
# @app.route('/register_client', methods=['POST'])
# def register_client():
#     data = request.get_json()
#
#     # Extract client data
#     client_id = data.get("client_id")
#     limit = data.get("limit")
#     interval = data.get("interval")
#     algorithm = data.get("algorithm", "token_bucket").lower()  # Default to token_bucket
#
#     # Check if all required fields are provided
#     if not client_id or not limit or not interval:
#         return jsonify({"error": "Missing required fields"}), 400
#
#     # Create rate-limiting algorithm object
#     if algorithm == "token_bucket":
#         algorithm_object = TokenBucket(limit, interval)
#     elif algorithm == "fixed_window":
#         algorithm_object = FixedWindowCounter(limit, interval)
#     else:
#         return jsonify({"error": "Invalid algorithm specified"}), 400
#
#     # Store the client configuration
#     clients[client_id] = {
#         "algorithm": algorithm_object
#     }
#
#     return jsonify({"message": f"Client {client_id} registered successfully with {algorithm} algorithm"}), 201
#
#
# @app.route('/validate_request', methods=['POST'])
# def validate_request():
#     data = request.get_json()
#     client_id = data.get("client_id")
#
#     # Check if the client exists
#     if client_id not in clients:
#         return jsonify({"error": "Client not found"}), 404
#
#     # Get client's algorithm object
#     client = clients[client_id]
#     algorithm = client["algorithm"]
#
#     # Check if the request is allowed based on the algorithm
#     if algorithm.allow_request():
#         return jsonify({"message": "Request allowed"}), 200
#     else:
#         return jsonify({"error": "Too many requests, rate limit exceeded"}), 429
#
#
# @app.route('/client_status/<client_id>', methods=['GET'])
# def client_status(client_id):
#     # Check if the client exists
#     if client_id not in clients:
#         return jsonify({"error": "Client not found"}), 404
#
#     # Get client's algorithm object
#     client = clients[client_id]
#     algorithm = client["algorithm"]
#
#     # Return current status (remaining requests)
#     if isinstance(algorithm, TokenBucket):
#         remaining_requests = algorithm.tokens
#     elif isinstance(algorithm, FixedWindowCounter):
#         remaining_requests = algorithm.limit - algorithm.request_count
#
#     return jsonify({
#         "client_id": client_id,
#         "remaining_requests": remaining_requests,
#         "limit": algorithm.limit,
#         "interval": algorithm.interval
#     }), 200
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
#
# # from flask import Flask, request, jsonify
# #
# # app = Flask(__name__)
# # #storage
# # clients = {}
# #
# # '''
# # {
# #   "client_id": "client123",
# #   "limit": 100,
# #   "interval": "minute"
# # }
# #
# # '''
# # @app.route('/register_client', methods=['POST'])
# # def register_client():
# #     data = request.get_json()
# #     client_id = data.get("client_id")
# #     limit = data.get("limit")
# #     interval = data.get("interval")
# #     if not client_id or not limit or not interval:
# #         return jsonify({"error": "Missing required fields"}), 400
# #     clients[client_id] = {
# #         "limit": limit,
# #         "interval": interval,
# #         "requests_made": 0
# #     }
# #
# #     return jsonify({"message": f"Client {client_id} registered successfully"}), 201
# #
# #
# # @app.route('/validate_request', methods=['POST'])
# # def validate_request():
# #     data = request.get_json()
# #     client_id = data.get("client_id")
# #     if client_id not in clients:
# #         return jsonify({"error": "Client not found"}), 404
# #     client = clients[client_id]
# #     if client['requests_made'] >= client['limit']:
# #         return jsonify({"error": "Too many requests, rate limit exceeded"}), 429
# #     client['requests_made'] += 1
# #
# #     return jsonify({"message": "Request allowed"}), 200
# #
# #
# # @app.route('/client_status/<client_id>', methods=['GET'])
# # def client_status(client_id):
# #     if client_id not in clients:
# #         return jsonify({"error": "Client not found"}), 404
# #     client = clients[client_id]
# #     remaining_requests = client['limit'] - client['requests_made']
# #
# #     return jsonify({
# #         "client_id": client_id,
# #         "remaining_requests": remaining_requests,
# #         "limit": client['limit'],
# #         "interval": client['interval']
# #     }), 200
# #
# #
# # if __name__ == '__main__':
# #     app.run(debug=True)
