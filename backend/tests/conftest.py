"""
Pytest configuration - MUST set environment before ANY imports.
"""
import os
import sys
from pathlib import Path

os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"

import pytest
from fastapi.testclient import TestClient
from app.main import app, SingletonResources


@pytest.fixture(scope="session")
def test_app():
    """Create a test app with initialized singleton resources."""
    # Initialize singleton resources for testing
    app.state.resources = SingletonResources()
    yield app
    # Cleanup after all tests
    if hasattr(app.state, 'resources') and app.state.resources:
        app.state.resources.cleanup()


@pytest.fixture(scope="function")
def client(test_app):
    """Create a test client for each test function."""
    with TestClient(test_app) as test_client:
        yield test_client
