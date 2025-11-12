"""
Pytest configuration and fixtures for FastAPI application testing.
"""

import os


os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"

from fastapi.testclient import TestClient
import pytest

from app.main import SingletonResources, app
from app.repositories.penalties_repo import PenaltiesRepository
from app.repositories.ratings_repo import RatingsRepository
from app.repositories.recommendations_repo import RecommendationsRepository
from app.repositories.users_repo import UsersRepository
from app.repositories.watchlist_repo import WatchlistRepository


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create a temporary directory for test data that persists across session."""
    return tmp_path_factory.mktemp("test_data")


@pytest.fixture(scope="session")
def test_repositories(test_data_dir):
    """Create test repositories using temporary files."""
    users_file = test_data_dir / "users.csv"
    ratings_file = test_data_dir / "ratings.json"
    recommendations_file = test_data_dir / "recommendations.json"
    penalties_file = test_data_dir / "penalties.json"
    watchlist_file = test_data_dir / "watchlist.json"

    return {
        "users_repo": UsersRepository(users_file=str(users_file)),
        "ratings_repo": RatingsRepository(ratings_file=str(ratings_file)),
        "recommendations_repo": RecommendationsRepository(recommendations_file=str(recommendations_file)),
        "penalties_repo": PenaltiesRepository(penalties_file=str(penalties_file)),
        "watchlist_repo": WatchlistRepository(watchlist_file=str(watchlist_file)),
    }


@pytest.fixture(scope="session")
def test_app(test_repositories):
    """Create a test app with initialized singleton resources using test repositories."""
    SingletonResources._instance = None
    SingletonResources._initialized = False

    app.state.resources = SingletonResources()

    # Replace user data repositories with test repositories
    # movies_repo uses production data (needed for ML recommendations and related tests)
    app.state.resources.users_repo = test_repositories["users_repo"]
    app.state.resources.ratings_repo = test_repositories["ratings_repo"]
    app.state.resources.recommendations_repo = test_repositories["recommendations_repo"]
    app.state.resources.penalties_repo = test_repositories["penalties_repo"]
    app.state.resources.watchlist_repo = test_repositories["watchlist_repo"]

    yield app

    if hasattr(app.state, "resources") and app.state.resources:
        app.state.resources.cleanup()


@pytest.fixture
def client(test_app):
    """Create a test client for each test function."""
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture
def clean_test_data(test_repositories):
    """
    Fixture to clean up test data before and after each test.
    Ensures test isolation by removing all users, ratings, recommendations, and penalties.
    """
    users_repo = test_repositories["users_repo"]
    ratings_repo = test_repositories["ratings_repo"]
    recommendations_repo = test_repositories["recommendations_repo"]
    penalties_repo = test_repositories["penalties_repo"]
    watchlist_repo = test_repositories["watchlist_repo"]

    def cleanup():
        all_users = users_repo.get_all()
        for user in all_users:
            user_id = user["id"]

            user_ratings = ratings_repo.get_by_user(user_id)
            for rating in user_ratings:
                ratings_repo.delete(rating["id"])

            recommendations_repo.clear_for_user(user_id)

            user_penalties = penalties_repo.get_by_user(user_id)
            for penalty in user_penalties:
                penalties_repo.delete(penalty["id"])

            users_repo.delete(user_id)

    cleanup()

    yield test_repositories

    cleanup()
