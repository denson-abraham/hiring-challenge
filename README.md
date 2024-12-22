# hiring-challenge
This repo is part of Hiring Challenges.

# Hiring Challenge - ATE - 01 :  


---

## **Hiring Challenge: Build and Test a Low-Level System Design**

### **Objective**
Evaluate the candidate's ability to:
1. Design and implement a low-level system using APIs.
2. Write comprehensive tests using **pytest**.
3. Handle performance considerations, data modeling, and modular design.

---

### **Challenge Description**

#### **Scenario**
You are tasked with building a **Rate Limiter System** as a microservice. A rate limiter is used to control the number of API requests a client can make within a given timeframe. Your system should:
1. Provide an API for other services to check if a request is allowed.
2. Support multiple rate-limiting algorithms.
3. Be scalable and performant.

---

### **Requirements**

#### **Part 1: API Design**
Implement the following endpoints:
1. **POST /register_client**  
   Register a new client with a unique `client_id` and their rate-limiting configuration.
   - **Body**:  
     ```json
     {
       "client_id": "client123",
       "limit": 100,
       "interval": "minute"
     }
     ```
   - **Description**: `limit` is the maximum number of requests, and `interval` specifies the timeframe (`minute`, `hour`, etc.).

2. **POST /validate_request**  
   Validate if a request from a given `client_id` can proceed.
   - **Body**:  
     ```json
     {
       "client_id": "client123"
     }
     ```
   - **Response**:  
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

#### **Part 2: System Design**
The system must support **two rate-limiting algorithms**:
1. **Token Bucket Algorithm**: Tokens are added at a fixed rate. Requests consume tokens.
2. **Fixed Window Counter**: Count requests in fixed intervals.

- **Configurable per client**: When registering a client, specify the algorithm to use.

#### **Part 3: Data Storage**
Use an in-memory data store like **Redis** to:
1. Track request counts and limits for each client.
2. Ensure high performance.

---

#### **Part 4: Testing with Pytest**
Write tests to ensure the following:
1. **Unit Tests**:
   - Validate each rate-limiting algorithm independently.
   - Handle edge cases, such as limits being exactly reached or exceeded.
2. **Integration Tests**:
   - Test the API endpoints.
   - Mock Redis to verify interactions.
3. **Performance Tests**:
   - Simulate a high volume of requests to test the system under load.
4. **Error Handling**:
   - Invalid client registrations.
   - Requests for non-existent clients.

---

### **Expectations**
1. **System Design**:
   - Efficient implementation of rate-limiting algorithms.
   - Proper use of Redis or similar for high-speed operations.
2. **Testing**:
   - Achieve at least 90% test coverage with pytest and pytest-cov.
   - Mock external dependencies like Redis.
3. **Code Quality**:
   - Clean and modular code.
   - Clear documentation and proper error handling.

---

### **Bonus Points**
1. Add **support for custom intervals** (e.g., 30 seconds, 15 minutes).
2. Use **Docker** to containerize the application.
3. Implement **distributed rate limiting** for scalability (e.g., across multiple Redis instances).
4. Deploy the system to a free platform like Heroku or Render.

---

### **Folder Structure**
```
rate_limiter/
    ├── app.py                  # Main application file
    ├── algorithms/
    │   ├── token_bucket.py     # Token Bucket implementation
    │   ├── fixed_window.py     # Fixed Window implementation
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

### **Evaluation Criteria**
1. **Functionality (40%)**:
   - Correct implementation of rate limiting and APIs.
   - Scalability and performance.

2. **Testing (40%)**:
   - Comprehensive test cases covering edge cases and performance.
   - High test coverage using pytest.

3. **System Design (20%)**:
   - Efficient and modular implementation of algorithms.
   - Proper use of Redis for data management.

---
