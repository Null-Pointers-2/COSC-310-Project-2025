"""Unit tests for singleton resources."""

import threading
from unittest.mock import Mock, patch

import pytest

from app.core.resources import SingletonResources


@pytest.fixture(autouse=True)
def reset_singleton():
    SingletonResources._instance = None
    SingletonResources._initialized = False
    yield
    SingletonResources._instance = None
    SingletonResources._initialized = False


def test_singleton_returns_same_instance():
    with (
        patch("app.core.resources.UsersRepository"),
        patch("app.core.resources.MoviesRepository"),
        patch("app.core.resources.RatingsRepository"),
        patch("app.core.resources.WatchlistRepository"),
        patch("app.core.resources.RecommendationsRepository"),
        patch("app.core.resources.PenaltiesRepository"),
        patch("app.core.resources.PasswordHasher"),
    ):
        instance1 = SingletonResources()
        instance2 = SingletonResources()
        assert instance1 is instance2


def test_singleton_initializes_once():
    mock_users = Mock()
    with (
        patch("app.core.resources.UsersRepository", return_value=mock_users),
        patch("app.core.resources.MoviesRepository"),
        patch("app.core.resources.RatingsRepository"),
        patch("app.core.resources.WatchlistRepository"),
        patch("app.core.resources.RecommendationsRepository"),
        patch("app.core.resources.PenaltiesRepository"),
        patch("app.core.resources.PasswordHasher"),
    ):
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

    with (
        patch("app.core.resources.UsersRepository", return_value=mock_users),
        patch("app.core.resources.MoviesRepository", return_value=mock_movies),
        patch("app.core.resources.RatingsRepository", return_value=mock_ratings),
        patch("app.core.resources.WatchlistRepository", return_value=mock_watchlist),
        patch("app.core.resources.RecommendationsRepository", return_value=mock_recommendations),
        patch("app.core.resources.PenaltiesRepository", return_value=mock_penalties),
        patch("app.core.resources.PasswordHasher", return_value=mock_hasher),
    ):
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
    with (
        patch("app.core.resources.UsersRepository", return_value=mock_users),
        patch("app.core.resources.MoviesRepository"),
        patch("app.core.resources.RatingsRepository"),
        patch("app.core.resources.WatchlistRepository"),
        patch("app.core.resources.RecommendationsRepository"),
        patch("app.core.resources.PenaltiesRepository"),
        patch("app.core.resources.PasswordHasher"),
    ):
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
    with (
        patch("app.core.resources.UsersRepository"),
        patch("app.core.resources.MoviesRepository"),
        patch("app.core.resources.RatingsRepository"),
        patch("app.core.resources.WatchlistRepository"),
        patch("app.core.resources.RecommendationsRepository"),
        patch("app.core.resources.PenaltiesRepository"),
        patch("app.core.resources.PasswordHasher", return_value=mock_hasher_instance),
    ):
        resources = SingletonResources()
        assert resources.password_hasher is mock_hasher_instance


def test_recommender_lazy_initialization():
    """Test that recommender is not initialized until accessed."""
    mock_recommender = Mock()
    with (
        patch("app.core.resources.UsersRepository"),
        patch("app.core.resources.MoviesRepository"),
        patch("app.core.resources.RatingsRepository"),
        patch("app.core.resources.WatchlistRepository"),
        patch("app.core.resources.RecommendationsRepository"),
        patch("app.core.resources.PenaltiesRepository"),
        patch("app.core.resources.PasswordHasher"),
        patch("app.core.resources.MovieRecommender", return_value=mock_recommender) as mock_recommender_class,
    ):
        resources = SingletonResources()

        mock_recommender_class.assert_not_called()
        _ = resources.recommender
        mock_recommender_class.assert_called_once()
