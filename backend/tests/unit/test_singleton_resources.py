"""Unit tests for resources singleton."""
from unittest.mock import Mock, patch
from app.main import SingletonResources
import pytest
import threading

@pytest.fixture
def patched_resources():
    with patch('app.main.UsersRepository') as mock_users, \
         patch('app.main.MoviesRepository') as mock_movies, \
         patch('app.main.RatingsRepository') as mock_ratings, \
         patch('app.main.WatchlistRepository') as mock_watchlist, \
         patch('app.main.RecommendationsRepository') as mock_recommendations, \
         patch('app.main.PenaltiesRepository') as mock_penalties, \
         patch('app.main.PasswordHasher') as mock_hasher:
        yield {
            "users": mock_users,
            "movies": mock_movies,
            "ratings": mock_ratings,
            "watchlist": mock_watchlist,
            "recommendations": mock_recommendations,
            "penalties": mock_penalties,
            "hasher": mock_hasher
        }



def test_singleton_returns_same_instance(patched_resources):

    SingletonResources._instance = None
    SingletonResources._initialized = False

    instance1 = SingletonResources()
    instance2 = SingletonResources()

    assert instance1 is instance2

def test_singleton_initializes_once(patched_resources):

    SingletonResources._instance = None
    SingletonResources._initialized = False

    instance1 = SingletonResources()
    instance2 = SingletonResources()
    instance3 = SingletonResources()

    mock_users_repo = patched_resources["users"]
    assert mock_users_repo.call_count == 1

def test_singleton_has_all_repositories(patched_resources):

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

    SingletonResources._instance = None
    SingletonResources._initialized = False

    resources = SingletonResources()

    resources.cleanup()

def test_singleton_thread_safety(patched_resources):

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
    mock_repo = Mock()

    SingletonResources._instance = None
    SingletonResources._initialized = False

    resources = SingletonResources()

    assert resources.users_repo is mock_repo

def test_password_hasher_initialized(patched_resources):
    mock_hasher_class = Mock()
    mock_hasher_instance = Mock()
    mock_hasher_class.return_value = mock_hasher_instance

    SingletonResources._instance = None
    SingletonResources._initialized = False

    resources = SingletonResources()

    mock_hasher_class.assert_called_once()
    assert resources.password_hasher is mock_hasher_instance