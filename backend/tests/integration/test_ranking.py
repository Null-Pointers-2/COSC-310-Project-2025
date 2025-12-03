import json
from datetime import UTC, datetime
from unittest.mock import mock_open, patch

from app.routers import ranking

MOCK_RATINGS = [
    {"movie_id": 1, "rating": 5.0},
    {"movie_id": 1, "rating": 5.0},
    {"movie_id": 1, "rating": 5.0},
    {"movie_id": 2, "rating": 1.0},
]

MOCK_TITLES = {1: "Test Toy Story", 2: "Test Jumanji"}


def test_calculate_weighted_rating_logic():
    with patch("app.routers.ranking.load_titles_from_csv", return_value=MOCK_TITLES):
        result = ranking.calculate_weighted_rating(MOCK_RATINGS)

        assert len(result) > 0
        assert result[0]["movie_id"] == 1
        assert result[0]["score"] > result[1]["score"]

        assert result[0]["title"] == "Test Toy Story"
        assert "tmdb_id" in result[0]


def test_get_popular_movies_success():
    ranking.popular_movies_cache = {"last_updated": None, "data": []}

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", mock_open(read_data=json.dumps(MOCK_RATINGS))),
        patch("app.routers.ranking.load_titles_from_csv", return_value=MOCK_TITLES),
    ):
        result = ranking.get_popular_movies()

        assert len(result) > 0
        assert result[0]["movie_id"] == 1
        assert result[0]["title"] == "Test Toy Story"


def test_get_popular_movies_no_file():
    ranking.popular_movies_cache = {"last_updated": None, "data": []}

    with patch("pathlib.Path.exists", return_value=False):
        result = ranking.get_popular_movies()
        assert result == []


def test_get_popular_movies_cached():
    mock_data = [{"movie_id": 99, "title": "Cached Movie"}]
    ranking.popular_movies_cache = {
        "last_updated": datetime.now(UTC),
        "data": mock_data,
    }

    with patch("app.routers.ranking.UPDATE_FREQUENCY", 24):
        result = ranking.get_popular_movies()
        assert result == mock_data
