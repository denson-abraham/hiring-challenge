# hiring-challenge
This repo is part of Hiring Challenges.

# Hiring Challenge - ATE - 01 :  

Certainly! Here's a refined version of your hiring challenge README, ensuring clarity and professionalism for potential candidates:

---

# Hiring Challenge: Build and Test a Low-Level System Design

## Objective

Evaluate the candidate's ability to:

1. Design and implement a low-level system using APIs.
2. Write comprehensive tests using **pytest**.
3. Address performance considerations, data modeling, and modular design.

---

## Challenge Description

### Scenario

Develop a **Rate Limiter System** as a microservice. A rate limiter controls the number of API requests a client can make within a specified timeframe. Your system should:

1. Provide an API for other services to check if a request is permitted.
2. Support multiple rate-limiting algorithms.
3. Be scalable and performant.

---

## Requirements

### Part 1: API Design

Implement the following endpoints:

1. **POST /register_client**  
   Register a new client with a unique `client_id` and their rate-limiting configuration.

   - **Request Body**:
     ```json
     {
       "client_id": "client123",
       "limit": 100,
       "interval": "minute"
     }
     ```
   - **Description**: `limit` denotes the maximum number of requests, and `interval` specifies the timeframe (e.g., `minute`, `hour`).

2. **POST /validate_request**  
   Determine if a request from a given `client_id` is permissible.

   - **Request Body**:
     ```json
     {
       "client_id": "client123"
     }
     ```
   - **Responses**:
     - `200 OK` if the request is allowed.
     - `429 Too Many Requests` if the request exceeds the limit.

3. **GET /client_status/{client_id}**  
   Retrieve the current usage and limit status for a client.

   - **Response**:
     ```json
     {
       "client_id": "client123",
       "remaining_requests": 85,
       "limit": 100,
       "interval": "minute"
     }
     ```

---

### Part 2: System Design

The system must support two rate-limiting algorithms:

1. **Token Bucket Algorithm**: Tokens are added at a fixed rate; requests consume tokens.
2. **Fixed Window Counter**: Counts requests within fixed intervals.

- **Client-Specific Configuration**: Specify the algorithm during client registration.

### Part 3: Data Storage

Utilize an in-memory data store, such as **Redis**, to:

1. Track request counts and limits for each client.
2. Ensure high performance.

---

### Part 4: Testing with Pytest

Develop tests to ensure:

1. **Unit Tests**:
   - Validate each rate-limiting algorithm independently.
   - Address edge cases, such as limits being exactly reached or exceeded.

2. **Integration Tests**:
   - Test the API endpoints.
   - Mock Redis to verify interactions.

3. **Performance Tests**:
   - Simulate a high volume of requests to assess system performance.

4. **Error Handling**:
   - Manage invalid client registrations.
   - Handle requests for non-existent clients.

---

## Expectations

1. **System Design**:
   - Efficient implementation of rate-limiting algorithms.
   - Appropriate use of Redis for high-speed operations.

2. **Testing**:
   - Achieve at least 90% test coverage using **pytest** and `pytest-cov`.
   - Mock external dependencies like Redis.

3. **Code Quality**:
   - Maintain clean and modular code.
   - Provide clear documentation and robust error handling.

---

## Bonus Points

1. Support custom intervals (e.g., 30 seconds, 15 minutes).
2. Containerize the application using **Docker**.
3. Implement distributed rate limiting for scalability (e.g., across multiple Redis instances).
4. Deploy the system to a free platform like **Heroku** or **Render**.

---

## Suggested Folder Structure

```
rate_limiter/
├── app.py                  # Main application file
├── algorithms/
│   ├── token_bucket.py     # Token Bucket implementation
│   └── fixed_window.py     # Fixed Window implementation
├── tests/
│   ├── test_algorithms.py  # Tests for rate-limiting algorithms
│   ├── test_api.py         # Tests for API endpoints
│   └── conftest.py         # Pytest fixtures
├── requirements.txt        # Dependencies
├── Dockerfile              # Docker configuration
├── README.md               # Instructions
└── .coveragerc             # Coverage configuration
```

---

## Evaluation Criteria

1. **Functionality (40%)**:
   - Accurate implementation of rate limiting and APIs.
   - Scalability and performance.

2. **Testing (40%)**:
   - Comprehensive test cases covering edge cases and performance.
   - High test coverage using **pytest**.

3. **System Design (20%)**:
   - Efficient and modular implementation of algorithms.
   - Effective use of Redis for data management.

---

Feel free to reach out if you have any questions or need further clarification. Good luck! 
