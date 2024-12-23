import pytest
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_register_client(client):
    response = client.post('/register_client', json={
        "client_id": "client123",
        "limit": 100,
        "interval": "1m",
        "algorithm": "token_bucket"
    })
    assert response.status_code == 201
    assert b"Client client123 registered successfully" in response.data

    # Test invalid registration
    response = client.post('/register_client', json={})
    assert response.status_code == 400
    assert b"Missing required fields" in response.data

    # Test invalid interval
    response = client.post('/register_client', json={
        "client_id": "client124",
        "limit": 100,
        "interval": "1x",
        "algorithm": "token_bucket"
    })
    assert response.status_code == 400
    assert b"Invalid interval format" in response.data

    # Test invalid Algorithm
    response = client.post('/register_client', json={
        "client_id": "client124",
        "limit": 100,
        "interval": "1m",
        "algorithm": "token_bucket_algorithm"
    })
    assert response.status_code == 400
    assert b"Invalid algorithm specified" in response.data


def test_validate_request_tokenbucket(client):
    client.post('/register_client', json={
        "client_id": "client123",
        "limit": 3,
        "interval": "1s",
        "algorithm": "token_bucket"
    })

    # Make requests within limit
    for _ in range(3):
        response = client.post('/validate_request', json={"client_id": "client123"})
        assert response.status_code == 200
        assert b"Request allowed" in response.data

    # Exceed limit
    response = client.post('/validate_request', json={"client_id": "client123"})
    assert response.status_code == 429
    assert b"Too many requests" in response.data

def test_validate_request_fixedwindow(client):
    client.post('/register_client', json={
        "client_id": "client123",
        "limit": 3,
        "interval": "1s",
        "algorithm": "fixed_window"
    })

    # Make requests within limit
    for _ in range(3):
        response = client.post('/validate_request', json={"client_id": "client123"})
        assert response.status_code == 200
        assert b"Request allowed" in response.data

    # Exceed limit
    response = client.post('/validate_request', json={"client_id": "client123"})
    assert response.status_code == 429
    assert b"Too many requests" in response.data

def test_client_status(client):
    client.post('/register_client', json={
        "client_id": "client123",
        "limit": 100,
        "interval": "1m",
        "algorithm": "token_bucket"
    })

    response = client.get('/client_status/client123')
    assert response.status_code == 200
    assert b"remaining_requests" in response.data

    # Non-existent client
    response = client.get('/client_status/nonexistent')
    assert response.status_code == 404
    assert b"Client not found" in response.data

def test_high_volume_requests(client):
    client.post('/register_client', json={
        "client_id": "client123",
        "limit": 100,
        "interval": "1s",
        "algorithm": "token_bucket"
    })

    # 100 requests
    allowed_requests = 0
    for _ in range(150):
        response = client.post('/validate_request', json={"client_id": "client123"})
        if response.status_code == 200:
            allowed_requests += 1

    assert allowed_requests == 100
