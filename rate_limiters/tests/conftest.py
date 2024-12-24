import pytest
from app import app as flask_app
from unittest.mock import MagicMock
import redis

@pytest.fixture
def app():
    """Fixture to provide the Flask app for testing."""
    yield flask_app

@pytest.fixture
def client(app):
    """Fixture to provide a test client for the Flask app."""
    return app.test_client()

@pytest.fixture
def mock_redis_client(monkeypatch):
    """
    Fixture to mock the Redis client used in the app.
    Replaces the redis.StrictRedis instance with a MagicMock.
    """
    mock_redis = MagicMock(spec=redis.StrictRedis)
    monkeypatch.setattr("app.redis_client", mock_redis)
    yield mock_redis
