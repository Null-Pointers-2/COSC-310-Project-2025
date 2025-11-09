"""Unit tests for SingletonResources class."""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestSingletonPattern:
    """Test the singleton pattern implementation."""

    def test_singleton_returns_same_instance(self):
        """Test that SingletonResources returns the same instance every time."""
        # Need to patch all repository imports before importing SingletonResources
        with patch('app.main.UsersRepository'), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import SingletonResources

            # Reset the singleton for testing
            SingletonResources._instance = None
            SingletonResources._initialized = False

            # Create two instances
            instance1 = SingletonResources()
            instance2 = SingletonResources()

            # They should be the same object
            assert instance1 is instance2

    def test_singleton_initializes_once(self):
        """Test that __init__ only runs once even with multiple instantiations."""
        with patch('app.main.UsersRepository') as mock_users_repo, \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import SingletonResources

            # Reset the singleton
            SingletonResources._instance = None
            SingletonResources._initialized = False

            # Create three instances
            instance1 = SingletonResources()
            instance2 = SingletonResources()
            instance3 = SingletonResources()

            # UsersRepository should only be called once
            assert mock_users_repo.call_count == 1

    def test_singleton_has_all_repositories(self):
        """Test that singleton initializes all required repositories."""
        with patch('app.main.UsersRepository') as mock_users, \
             patch('app.main.MoviesRepository') as mock_movies, \
             patch('app.main.RatingsRepository') as mock_ratings, \
             patch('app.main.WatchlistRepository') as mock_watchlist, \
             patch('app.main.RecommendationsRepository') as mock_recommendations, \
             patch('app.main.PenaltiesRepository') as mock_penalties, \
             patch('app.main.PasswordHasher') as mock_hasher:

            from app.main import SingletonResources

            # Reset the singleton
            SingletonResources._instance = None
            SingletonResources._initialized = False

            # Create instance
            resources = SingletonResources()

            # Verify all repositories are initialized
            assert hasattr(resources, 'users_repo')
            assert hasattr(resources, 'movies_repo')
            assert hasattr(resources, 'ratings_repo')
            assert hasattr(resources, 'watchlist_repo')
            assert hasattr(resources, 'recommendations_repo')
            assert hasattr(resources, 'penalties_repo')
            assert hasattr(resources, 'password_hasher')

    def test_singleton_cleanup_method(self):
        """Test that cleanup method exists and can be called."""
        with patch('app.main.UsersRepository'), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import SingletonResources

            # Reset the singleton
            SingletonResources._instance = None
            SingletonResources._initialized = False

            resources = SingletonResources()

            # Should not raise any exceptions
            resources.cleanup()

    def test_singleton_thread_safety(self):
        """Test that singleton works correctly with concurrent access."""
        import threading

        with patch('app.main.UsersRepository'), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import SingletonResources

            # Reset the singleton
            SingletonResources._instance = None
            SingletonResources._initialized = False

            instances = []

            def create_instance():
                instances.append(SingletonResources())

            # Create 10 threads that all try to create instances
            threads = [threading.Thread(target=create_instance) for _ in range(10)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            # All instances should be the same object
            first_instance = instances[0]
            for instance in instances:
                assert instance is first_instance


class TestSingletonRepositories:
    """Test that singleton properly initializes repository instances."""

    def test_users_repository_initialized(self):
        """Test that users repository is properly initialized."""
        mock_repo = Mock()
        with patch('app.main.UsersRepository', return_value=mock_repo), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher'):

            from app.main import SingletonResources

            SingletonResources._instance = None
            SingletonResources._initialized = False

            resources = SingletonResources()

            assert resources.users_repo is mock_repo

    def test_password_hasher_initialized(self):
        """Test that password hasher is properly initialized."""
        mock_hasher_class = Mock()
        mock_hasher_instance = Mock()
        mock_hasher_class.recommended.return_value = mock_hasher_instance

        with patch('app.main.UsersRepository'), \
             patch('app.main.MoviesRepository'), \
             patch('app.main.RatingsRepository'), \
             patch('app.main.WatchlistRepository'), \
             patch('app.main.RecommendationsRepository'), \
             patch('app.main.PenaltiesRepository'), \
             patch('app.main.PasswordHasher', mock_hasher_class):

            from app.main import SingletonResources

            SingletonResources._instance = None
            SingletonResources._initialized = False

            resources = SingletonResources()

            # Verify PasswordHasher.recommended() was called
            mock_hasher_class.recommended.assert_called_once()
            assert resources.password_hasher is mock_hasher_instance
