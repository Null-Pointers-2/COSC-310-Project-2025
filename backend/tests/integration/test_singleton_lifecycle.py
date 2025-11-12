"""Integration tests for SingletonResources lifecycle with FastAPI."""

from unittest.mock import Mock

from fastapi.testclient import TestClient
import pytest

from app.main import SingletonResources, app


@pytest.fixture
def reset_singleton():
    """Reset singleton state before and after test."""
    SingletonResources._instance = None
    SingletonResources._initialized = False
    yield
    SingletonResources._instance = None
    SingletonResources._initialized = False


def test_singleton_initialized_on_startup(client):
    assert app.state.resources is not None
    assert hasattr(app.state.resources, "users_repo")
    assert hasattr(app.state.resources, "movies_repo")


def test_singleton_available_in_app_state(client):
    response = client.get("/health")
    assert response.status_code == 200

    assert hasattr(app.state, "resources")
    resources = app.state.resources
    assert resources is not None


def test_singleton_cleanup_called_on_shutdown(reset_singleton, test_data_dir):
    mock_cleanup = Mock()

    with TestClient(app) as test_client:
        app.state.resources.cleanup = mock_cleanup
        response = test_client.get("/health")
        assert response.status_code == 200

    mock_cleanup.assert_called_once()


def test_singleton_persists_across_requests(client):
    client.get("/health")
    first_resources = app.state.resources

    client.get("/health")
    client.get("/")
    second_resources = app.state.resources

    assert first_resources is second_resources
    assert first_resources is not None


def test_global_resources_variable_set(client):
    assert hasattr(app.state, "resources")
    assert app.state.resources is not None


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
