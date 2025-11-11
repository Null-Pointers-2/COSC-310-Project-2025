"""
Pytest configuration and fixtures for FastAPI application testing.
"""

import os


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

    yield app

    if hasattr(app.state, "resources") and app.state.resources:
        app.state.resources.cleanup()


@pytest.fixture(scope="function")
def client(test_app):
    """Create a test client for each test function."""
    with TestClient(test_app) as test_client:
        yield test_client
