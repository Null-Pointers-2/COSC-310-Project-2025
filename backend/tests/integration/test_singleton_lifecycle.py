"""Integration tests for SingletonResources lifecycle with FastAPI."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock


class TestSingletonLifecycle:
    """Test singleton integration with FastAPI startup/shutdown events."""

    def test_singleton_initialized_on_startup(self):
        """Test that singleton is initialized when FastAPI app starts."""
        with patch('app.main.UsersRepository'), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import app, resources

            # Create test client (triggers startup event)
            with TestClient(app) as client:
                # Verify singleton was initialized
                assert app.state.resources is not None
                assert hasattr(app.state.resources, 'users_repo')
                assert hasattr(app.state.resources, 'movies_repo')

    def test_singleton_available_in_app_state(self):
        """Test that singleton is accessible via app.state.resources."""
        with patch('app.main.UsersRepository'), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import app

            with TestClient(app) as client:
                # Make a request to verify app is running
                response = client.get("/health")
                assert response.status_code == 200

                # Verify resources are in app.state
                assert hasattr(app.state, 'resources')
                resources = app.state.resources
                assert resources is not None

    def test_singleton_cleanup_called_on_shutdown(self):
        """Test that cleanup is called when FastAPI app shuts down."""
        mock_cleanup = Mock()

        with patch('app.main.UsersRepository'), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import app

            with TestClient(app) as client:
                # Patch the cleanup method after initialization
                app.state.resources.cleanup = mock_cleanup

                # Make a request to ensure app is running
                client.get("/health")

            # After context manager exits, shutdown should have been called
            # and cleanup should have been invoked
            mock_cleanup.assert_called_once()

    def test_singleton_persists_across_requests(self):
        """Test that the same singleton instance is used across multiple requests."""
        with patch('app.main.UsersRepository') as mock_users_repo, \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import app

            with TestClient(app) as client:
                # Get the resources instance after first request
                client.get("/health")
                first_resources = app.state.resources

                # Make more requests
                client.get("/health")
                client.get("/")
                second_resources = app.state.resources

                # Should be the same instance
                assert first_resources is second_resources

                # Repository should only be initialized once
                assert mock_users_repo.call_count == 1

    def test_global_resources_variable_set(self):
        """Test that the global resources variable is set on startup."""
        with patch('app.main.UsersRepository'), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            import app.main

            # Initially resources should be None
            app.main.resources = None

            with TestClient(app.main.app) as client:
                # After startup, resources should be set
                assert app.main.resources is not None
                assert app.main.resources is app.main.app.state.resources


class TestSingletonEndpointAccess:
    """Test that endpoints can access singleton resources."""

    def test_health_endpoint_works_with_singleton(self):
        """Test that health endpoint works when singleton is initialized."""
        with patch('app.main.UsersRepository'), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import app

            with TestClient(app) as client:
                response = client.get("/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"

    def test_root_endpoint_works_with_singleton(self):
        """Test that root endpoint works when singleton is initialized."""
        with patch('app.main.UsersRepository'), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import app

            with TestClient(app) as client:
                response = client.get("/")
                assert response.status_code == 200
                data = response.json()
                assert data["message"] == "Movie Recommendations API"


class TestSingletonErrorHandling:
    """Test error handling for singleton initialization."""

    def test_app_handles_repository_initialization_error(self):
        """Test that app can handle errors during repository initialization."""
        with patch('app.main.UsersRepository', side_effect=Exception("Init error")), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import app, SingletonResources

            # Reset singleton
            SingletonResources._instance = None
            SingletonResources._initialized = False

            # This should raise an error during startup
            with pytest.raises(Exception, match="Init error"):
                with TestClient(app) as client:
                    pass

    def test_cleanup_handles_none_resources(self):
        """Test that shutdown handles case where resources is None."""
        with patch('app.main.UsersRepository'), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            import app.main

            # Set resources to None
            app.main.resources = None

            with TestClient(app.main.app) as client:
                # Override to set resources back to None
                app.main.resources = None

            # Should not raise an error - cleanup checks for None
