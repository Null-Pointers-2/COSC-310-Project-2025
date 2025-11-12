"""
Pytest configuration and fixtures for FastAPI application testing.
"""

import os
from unittest.mock import Mock


os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"

from fastapi.testclient import TestClient
import pytest

from app.main import SingletonResources, app


@pytest.fixture(scope="session")
def test_app():
    """Create a test app with initialized singleton resources."""
    SingletonResources._instance = None
    SingletonResources._initialized = False

    app.state.resources = SingletonResources()

    mock_recommender = Mock()
    mock_recommender.get_similar_by_id.return_value = []
    app.state.resources._recommender = mock_recommender

    yield app

    if hasattr(app.state, "resources") and app.state.resources:
        app.state.resources.cleanup()


@pytest.fixture
def client(test_app):
    """Create a test client for each test function."""
    with TestClient(test_app) as test_client:
        yield test_client
