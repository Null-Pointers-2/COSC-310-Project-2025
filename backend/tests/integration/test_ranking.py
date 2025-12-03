import json
from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import MagicMock, mock_open, patch

from app.services import ranking_service

MOCK_RATINGS = [
    {"movie_id": 1, "rating": 5.0},
    {"movie_id": 1, "rating": 5.0},
    {"movie_id": 1, "rating": 5.0},
    {"movie_id": 2, "rating": 1.0},
]


def mock_get_by_id(movie_id):
    """Helper to mock the repository response"""
    titles = {1: "Test Toy Story", 2: "Test Jumanji"}
    if movie_id in titles:
        return {"title": titles[movie_id], "tmdb_id": 12345}
    return None


def test_calculate_weighted_rating_logic():
    mock_resources = MagicMock()
    mock_resources.movies_repo.get_by_id.side_effect = mock_get_by_id

    ranking_service._popular_cache = {"last_updated": None, "data": []}

    with patch("app.services.ranking_service.Path") as mock_path:
        mock_path_instance = mock_path.return_value
        mock_path_instance.exists.return_value = True
        mock_path_instance.open = mock_open(read_data=json.dumps(MOCK_RATINGS))

        result = ranking_service.get_popular_movies(mock_resources)

        assert len(result) > 0
        assert result[0]["movie_id"] == 1
        assert result[0]["score"] > result[1]["score"]

        assert result[0]["title"] == "Test Toy Story"
        assert result[0]["tmdb_id"] == 12345


def test_get_popular_movies_no_file():
    mock_resources = MagicMock()
    ranking_service._popular_cache = {"last_updated": None, "data": []}

    with patch("app.services.ranking_service.Path") as mock_patch:
        mock_path_instance = mock_patch.return_value
        mock_path_instance.exists.return_value = False

        result = ranking_service.get_popular_movies(mock_resources)
        assert result == []


def test_get_popular_movies_cached():
    mock_resources = MagicMock()

    mock_data = [{"movie_id": 99, "title": "Cached Movie"}]
    ranking_service._popular_cache = {
        "last_updated": datetime.now(UTC),
        "data": mock_data,
    }

    with patch("app.services.ranking_service.UPDATE_FREQUENCY_HOURS", 24):
        result = ranking_service.get_popular_movies(mock_resources)

        assert result == mock_data
        assert result[0]["title"] == "Cached Movie"


def test_get_popular_movies_cache_expired():
    mock_resources = MagicMock()
    mock_resources.movies_repo.get_by_id.side_effect = mock_get_by_id

    old_time = datetime.now(UTC) - timedelta(hours=25)
    ranking_service._popular_cache = {"last_updated": old_time, "data": [{"movie_id": 99, "title": "Old Data"}]}

    with patch("app.services.ranking_service.Path") as mock_patch:
        mock_path_instance = mock_patch.return_value
        mock_path_instance.exists.return_value = True
        mock_path_instance.open = mock_open(read_data=json.dumps(MOCK_RATINGS))

        result = ranking_service.get_popular_movies(mock_resources)

        assert result[0]["title"] == "Test Toy Story"
