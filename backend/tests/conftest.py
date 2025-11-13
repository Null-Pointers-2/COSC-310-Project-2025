"""
Pytest configuration and fixtures for FastAPI application testing.
"""

import os

os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_resources
from app.core.resources import SingletonResources
from app.main import app
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
def override_app_resources(test_repositories):
    """
    Overrides the app's 'get_resources' dependency for the entire session to return a SingletonResources object populated with shared test repositories.
    """
    mock_resources = SingletonResources()

    for repo_name, repo_instance in test_repositories.items():
        if repo_instance is not None:
            setattr(mock_resources, repo_name, repo_instance)

    def mock_get_resources():
        return mock_resources

    app.dependency_overrides[get_resources] = mock_get_resources

    yield

    del app.dependency_overrides[get_resources]


@pytest.fixture
def client(override_app_resources):
    """Create a test client for each test function."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def clean_test_data(test_repositories):
    """Fixture to clean up test data before and after each test."""

    def cleanup():
        test_repositories["users_repo"].save_all([])
        test_repositories["ratings_repo"].save_data([])
        test_repositories["recommendations_repo"].save_data({})
        test_repositories["penalties_repo"].save_data([])
        test_repositories["watchlist_repo"].save_data({})

    cleanup()
    yield test_repositories
    cleanup()
