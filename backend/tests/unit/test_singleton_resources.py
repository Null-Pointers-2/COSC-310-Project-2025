"""Unit tests for SingletonResources class."""
from unittest.mock import Mock, patch
from app.main import SingletonResources
import pytest

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


def test_singleton_returns_same_instance(patched_resources):
    """Test that SingletonResources returns the same instance every time."""
    with patch('app.main.UsersRepository'), \
            patch('app.main.MoviesRepository'), \
            patch('app.main.RatingsRepository'), \
            patch('app.main.WatchlistRepository'), \
            patch('app.main.RecommendationsRepository'), \
            patch('app.main.PenaltiesRepository'), \
            patch('app.main.PasswordHasher'):

        SingletonResources._instance = None
        SingletonResources._initialized = False

        instance1 = SingletonResources()
        instance2 = SingletonResources()

        assert instance1 is instance2

def test_singleton_initializes_once(patched_resources):
    """Test that __init__ only runs once even with multiple instantiations."""
    with patch('app.main.UsersRepository') as mock_users_repo, \
            patch('app.main.MoviesRepository'), \
            patch('app.main.RatingsRepository'), \
            patch('app.main.WatchlistRepository'), \
            patch('app.main.RecommendationsRepository'), \
            patch('app.main.PenaltiesRepository'), \
            patch('app.main.PasswordHasher'):

        from app.main import SingletonResources

        SingletonResources._instance = None
        SingletonResources._initialized = False

        instance1 = SingletonResources()
        instance2 = SingletonResources()
        instance3 = SingletonResources()

        assert mock_users_repo.call_count == 1

def test_singleton_has_all_repositories(patched_resources):
    """Test that singleton initializes all required repositories."""
    with patch('app.main.UsersRepository') as mock_users, \
            patch('app.main.MoviesRepository') as mock_movies, \
            patch('app.main.RatingsRepository') as mock_ratings, \
            patch('app.main.WatchlistRepository') as mock_watchlist, \
            patch('app.main.RecommendationsRepository') as mock_recommendations, \
            patch('app.main.PenaltiesRepository') as mock_penalties, \
            patch('app.main.PasswordHasher') as mock_hasher:

        SingletonResources._instance = None
        SingletonResources._initialized = False

        resources = SingletonResources()

        assert hasattr(resources, 'users_repo')
        assert hasattr(resources, 'movies_repo')
        assert hasattr(resources, 'ratings_repo')
        assert hasattr(resources, 'watchlist_repo')
        assert hasattr(resources, 'recommendations_repo')
        assert hasattr(resources, 'penalties_repo')
        assert hasattr(resources, 'password_hasher')

def test_singleton_cleanup_method(patched_resources):
    """Test that cleanup method exists and can be called."""
    with patch('app.main.UsersRepository'), \
            patch('app.main.MoviesRepository'), \
            patch('app.main.RatingsRepository'), \
            patch('app.main.WatchlistRepository'), \
            patch('app.main.RecommendationsRepository'), \
            patch('app.main.PenaltiesRepository'), \
            patch('app.main.PasswordHasher'):

        SingletonResources._instance = None
        SingletonResources._initialized = False

        resources = SingletonResources()

        resources.cleanup()

def test_singleton_thread_safety(patched_resources):
    """Test that singleton works correctly with concurrent access."""
    import threading

    with patch('app.main.UsersRepository'), \
            patch('app.main.MoviesRepository'), \
            patch('app.main.RatingsRepository'), \
            patch('app.main.WatchlistRepository'), \
            patch('app.main.RecommendationsRepository'), \
            patch('app.main.PenaltiesRepository'), \
            patch('app.main.PasswordHasher'):

        SingletonResources._instance = None
        SingletonResources._initialized = False

        instances = []

        threads = [threading.Thread(target=instances.append(SingletonResources())) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        first_instance = instances[0]
        for instance in instances:
            assert instance is first_instance

def test_users_repository_initialized(patched_resources):
    """Test that users repository is properly initialized."""
    mock_repo = Mock()
    with patch('app.main.UsersRepository', return_value=mock_repo), \
            patch('app.main.MoviesRepository'), \
            patch('app.main.RatingsRepository'), \
            patch('app.main.WatchlistRepository'), \
            patch('app.main.RecommendationsRepository'), \
            patch('app.main.PenaltiesRepository'), \
            patch('app.main.PasswordHasher'):

        SingletonResources._instance = None
        SingletonResources._initialized = False

        resources = SingletonResources()

        assert resources.users_repo is mock_repo

def test_password_hasher_initialized(patched_resources):
    """Test that password hasher is properly initialized."""
    mock_hasher_class = Mock()
    mock_hasher_instance = Mock()
    mock_hasher_class.return_value = mock_hasher_instance

    with patch('app.main.UsersRepository'), \
            patch('app.main.MoviesRepository'), \
            patch('app.main.RatingsRepository'), \
            patch('app.main.WatchlistRepository'), \
            patch('app.main.RecommendationsRepository'), \
            patch('app.main.PenaltiesRepository'), \
            patch('app.main.PasswordHasher', mock_hasher_class):

        SingletonResources._instance = None
        SingletonResources._initialized = False

        resources = SingletonResources()

        mock_hasher_class.assert_called_once()
        assert resources.password_hasher is mock_hasher_instance