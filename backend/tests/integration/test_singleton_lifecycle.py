"""Integration tests for SingletonResources lifecycle with FastAPI."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app, SingletonResources

@pytest.fixture
def patched_resources():
    with patch("app.main.UsersRepository"), \
         patch("app.main.MoviesRepository"), \
         patch("app.main.RatingsRepository"), \
         patch("app.main.WatchlistRepository"), \
         patch("app.main.RecommendationsRepository"), \
         patch("app.main.PenaltiesRepository"), \
         patch("app.main.PasswordHasher"):
        yield

class TestSingletonLifecycle:
    """Test singleton integration with FastAPI startup/shutdown events."""

    def test_singleton_initialized_on_startup(self, patched_resources):
        """Test that singleton is initialized when FastAPI app starts."""
        with TestClient(app) as client:
                assert app.state.resources is not None
                assert hasattr(app.state.resources, 'users_repo')
                assert hasattr(app.state.resources, 'movies_repo')

    def test_singleton_available_in_app_state(self, patched_resources):
        """Test that singleton is accessible via app.state.resources."""

        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200

            assert hasattr(app.state, 'resources')
            resources = app.state.resources
            assert resources is not None

    def test_singleton_cleanup_called_on_shutdown(self, patched_resources):
        """Test that cleanup is called when FastAPI app shuts down."""
        mock_cleanup = Mock()

        with TestClient(app) as client:
            app.state.resources.cleanup = mock_cleanup
            client.get("/health")

        mock_cleanup.assert_called_once()

    def test_singleton_persists_across_requests(self, test_app, client):
        """Test that the same singleton instance is used across multiple requests."""
        client.get("/health")
        first_resources = test_app.state.resources

        client.get("/health")
        client.get("/")
        second_resources = test_app.state.resources

        assert first_resources is second_resources
        assert first_resources is not None

    def test_global_resources_variable_set(self, test_app):
        """Test that resources are set in app.state on startup."""
        assert hasattr(test_app.state, 'resources')
        assert test_app.state.resources is not None

    def test_health_endpoint_works_with_singleton(self, patched_resources):
        """Test that health endpoint works when singleton is initialized."""

        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_root_endpoint_works_with_singleton(self, patched_resources):
        """Test that root endpoint works when singleton is initialized."""

        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Movie Recommendations API"

    def test_app_handles_repository_initialization_error(self):
        """Test that app can handle errors during repository initialization."""
        with patch('app.main.UsersRepository', side_effect=Exception("Init error")), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            SingletonResources._instance = None
            SingletonResources._initialized = False

            with pytest.raises(Exception, match="Init error"):
                with TestClient(app) as client:
                    pass