"""Unit tests for user insights service."""

from unittest.mock import Mock

from app.services.user_insights_service import (
    _analyze_genres,
    _analyze_watchlist_metrics,
    _calculate_preference_score,
    generate_user_insights,
)


def test_preference_score_basic():
    score = _calculate_preference_score(count=5, avg_rating=4.0, total_count=10)
    assert 66 <= score <= 67


def test_preference_score_perfect():
    score = _calculate_preference_score(count=10, avg_rating=5.0, total_count=10)
    assert score == 100.0


def test_preference_score_zero_total():
    score = _calculate_preference_score(count=0, avg_rating=5.0, total_count=0)
    assert score == 0.0


def test_analyze_genres():
    resources = Mock()
    resources.ratings_repo.get_by_user.return_value = [
        {"movie_id": 1, "rating": 5.0},
        {"movie_id": 2, "rating": 4.0},
    ]
    resources.watchlist_repo.get_by_user.return_value = [{"movie_id": 1}]
    resources.movies_repo.get_by_id.return_value = {"genres": ["Action"]}

    top_genre, top_3, insights = _analyze_genres(resources, "user123")

    assert top_genre == "Action"
    assert "Action" in top_3


def test_analyze_genres_no_ratings():
    resources = Mock()
    resources.ratings_repo.get_by_user.return_value = []
    resources.watchlist_repo.get_by_user.return_value = []

    top_genre, top_3, insights = _analyze_genres(resources, "user123")

    assert top_genre is None
    assert top_3 == []


def test_watchlist_metrics():
    resources = Mock()
    resources.watchlist_repo.get_by_user.return_value = [
        {"movie_id": 1, "added_at": "2024-01-01T00:00:00Z"},
        {"movie_id": 2, "added_at": "2024-01-02T00:00:00Z"},
    ]
    resources.ratings_repo.get_by_user.return_value = [
        {"movie_id": 1, "rating": 5.0, "timestamp": "2024-01-01T01:00:00Z"},
    ]
    resources.movies_repo.get_by_id.return_value = {"genres": ["Action"]}

    metrics = _analyze_watchlist_metrics(resources, "user123")

    assert metrics.total_watchlist_items == 2
    assert metrics.items_rated == 1
    assert metrics.completion_rate == 50.0


def test_generate_insights_user_not_found():
    resources = Mock()
    resources.users_repo.get_by_id.return_value = None

    insights = generate_user_insights(resources, "nonexistent", force_refresh=False)

    assert insights is None


def test_generate_insights_uses_cache():
    resources = Mock()
    resources.users_repo.get_by_id.return_value = {"id": "user123"}
    resources.user_insights_repo.get_by_user_id.return_value = {
        "user_id": "user123",
        "generated_at": "2024-01-01T00:00:00Z",
        "top_genre": "Action",
        "top_3_genres": ["Action"],
        "genre_insights": [],
        "top_theme": "original",
        "top_5_themes": ["original"],
        "theme_insights": [],
        "watchlist_metrics": {
            "total_watchlist_items": 0,
            "items_rated": 0,
            "items_not_rated": 0,
            "completion_rate": 0.0,
            "average_rating": None,
            "average_time_to_rate_hours": None,
            "genres_in_watchlist": [],
            "most_common_watchlist_genre": None,
        },
        "total_ratings": 5,
        "average_rating": 4.0,
        "rating_consistency": 0.5,
    }

    insights = generate_user_insights(resources, "user123", force_refresh=False)

    assert insights.user_id == "user123"
    resources.user_insights_repo.save.assert_not_called()
