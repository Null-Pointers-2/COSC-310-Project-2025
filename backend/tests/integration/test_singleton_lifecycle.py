"""Integration tests for SingletonResources lifecycle with FastAPI."""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import SingletonResources, app


@pytest.fixture
def reset_singleton():
    SingletonResources._instance = None
    SingletonResources._initialized = False
    if hasattr(app.state, "resources"):
        delattr(app.state, "resources")

    yield

    SingletonResources._instance = None
    SingletonResources._initialized = False
    if hasattr(app.state, "resources"):
        delattr(app.state, "resources")


def test_singleton_initialized_on_startup(client):
    assert hasattr(app.state, "resources")
    assert app.state.resources is not None

    resources = app.state.resources
    assert hasattr(resources, "users_repo")
    assert hasattr(resources, "movies_repo")


def test_singleton_available_in_app_state(client):
    response = client.get("/health")
    assert response.status_code == 200

    assert hasattr(app.state, "resources")
    assert app.state.resources is not None


def test_singleton_persists_across_requests(client):
    client.get("/health")
    first_resources = app.state.resources

    client.get("/health")
    client.get("/")
    second_resources = app.state.resources

    assert first_resources is second_resources
    assert first_resources is not None


def test_health_endpoint_works_with_singleton(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint_works_with_singleton(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Movie Recommendations API"


def test_singleton_cleanup_called_on_shutdown(reset_singleton):
    mock_cleanup = Mock()

    with TestClient(app) as test_client:
        app.state.resources = SingletonResources()
        app.state.resources.cleanup = mock_cleanup

        response = test_client.get("/health")
        assert response.status_code == 200

    mock_cleanup.assert_called_once()


def test_singleton_reinitializes_after_reset(reset_singleton):
    first_instance = SingletonResources()
    SingletonResources._instance = None
    SingletonResources._initialized = False

    second_instance = SingletonResources()

    assert first_instance is not second_instance
    assert isinstance(second_instance, SingletonResources)
