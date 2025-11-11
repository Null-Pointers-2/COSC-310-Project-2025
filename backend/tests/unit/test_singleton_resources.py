"""Unit tests for singleton resources."""
from unittest.mock import Mock, patch
import threading
import pytest
from app.main import SingletonResources

@pytest.fixture(autouse=True)
def reset_singleton():
    SingletonResources._instance = None
    SingletonResources._initialized = False
    yield
    SingletonResources._instance = None
    SingletonResources._initialized = False

def test_singleton_returns_same_instance():
    instance1 = SingletonResources()
    instance2 = SingletonResources()
    assert instance1 is instance2

def test_singleton_initializes_once():
    mock_users = Mock()
    with patch("app.main.UsersRepository", return_value=mock_users):
        instance1 = SingletonResources()
        instance2 = SingletonResources()
        app_users_repo_instance = instance1.users_repo
        assert app_users_repo_instance is mock_users

def test_singleton_has_all_repositories():
    mock_users = Mock()
    mock_movies = Mock()
    mock_ratings = Mock()
    mock_watchlist = Mock()
    mock_recommendations = Mock()
    mock_penalties = Mock()
    mock_hasher = Mock()

    with patch("app.main.UsersRepository", return_value=mock_users), \
         patch("app.main.MoviesRepository", return_value=mock_movies), \
         patch("app.main.RatingsRepository", return_value=mock_ratings), \
         patch("app.main.WatchlistRepository", return_value=mock_watchlist), \
         patch("app.main.RecommendationsRepository", return_value=mock_recommendations), \
         patch("app.main.PenaltiesRepository", return_value=mock_penalties), \
         patch("app.main.PasswordHasher", return_value=mock_hasher):
        resources = SingletonResources()

        assert resources.users_repo is mock_users
        assert resources.movies_repo is mock_movies
        assert resources.ratings_repo is mock_ratings
        assert resources.watchlist_repo is mock_watchlist
        assert resources.recommendations_repo is mock_recommendations
        assert resources.penalties_repo is mock_penalties
        assert resources.password_hasher is mock_hasher

def test_singleton_thread_safety():
    mock_users = Mock()
    with patch("app.main.UsersRepository", return_value=mock_users):
        instances = []

        def create_instance():
            instances.append(SingletonResources())

        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        first_instance = instances[0]
        for instance in instances:
            assert instance is first_instance


def test_password_hasher_initialized():
    mock_hasher_instance = Mock()
    with patch("app.main.PasswordHasher", return_value=mock_hasher_instance):
        resources = SingletonResources()
        assert resources.password_hasher is mock_hasher_instance
