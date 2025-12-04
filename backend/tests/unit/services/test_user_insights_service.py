"""Unit tests for user insights service."""

from unittest.mock import Mock

from app.services.user_insights_service import (
    _analyze_genres_from_ratings,
    _analyze_themes_from_ratings,
    _analyze_watchlist_metrics,
    _calculate_preference_score,
    generate_user_insights,
    get_user_insights_summary,
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
    all_ratings = [
        {"movie_id": 1, "rating": 5.0},
        {"movie_id": 2, "rating": 4.0},
    ]
    resources.watchlist_repo.get_by_user.return_value = [{"movie_id": 1}]
    resources.movies_repo.get_by_id.return_value = {"genres": ["Action"]}

    top_genre, top_3, _insights = _analyze_genres_from_ratings(resources, "user123", all_ratings)

    assert top_genre == "Action"
    assert "Action" in top_3


def test_analyze_genres_no_ratings():
    resources = Mock()
    all_ratings = []
    resources.watchlist_repo.get_by_user.return_value = []

    top_genre, top_3, _insights = _analyze_genres_from_ratings(resources, "user123", all_ratings)

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

    insights = generate_user_insights(resources, "nonexistent")

    assert insights is None


def test_analyze_genres_multiple_genres():
    """Test genre analysis with multiple genres."""
    resources = Mock()
    all_ratings = [
        {"movie_id": 1, "rating": 5.0},
        {"movie_id": 2, "rating": 4.0},
    ]
    resources.watchlist_repo.get_by_user.return_value = [{"movie_id": 1}]

    def get_movie(movie_id):
        return {"genres": ["Action", "Sci-Fi"]} if movie_id == 1 else {"genres": ["Drama"]}

    resources.movies_repo.get_by_id.side_effect = get_movie

    top_genre, _top_3, insights = _analyze_genres_from_ratings(resources, "user123", all_ratings)

    assert top_genre is not None
    assert len(insights) > 0


def test_analyze_themes_basic():
    """Test basic theme analysis."""
    resources = Mock()
    all_ratings = [{"movie_id": 1, "rating": 4.5}]
    resources.genome_repo.get_top_tags_for_movies.return_value = [
        {"tag_id": 1, "tag": "original", "movie_count": 1, "avg_relevance": 0.8},
    ]
    resources.genome_repo.get_movie_tags.return_value = [{"tag_id": 1}]

    top_theme, _top_5, _insights = _analyze_themes_from_ratings(resources, "user123", all_ratings)

    assert top_theme is not None


def test_analyze_themes_no_high_rated():
    """Test theme analysis with no high-rated movies."""
    resources = Mock()
    all_ratings = [{"movie_id": 1, "rating": 2.0}]

    top_theme, _top_5, insights = _analyze_themes_from_ratings(resources, "user123", all_ratings)

    assert top_theme is None
    assert insights == []


def test_analyze_themes_no_tags():
    """Test theme analysis when no tags found."""
    resources = Mock()
    all_ratings = [{"movie_id": 1, "rating": 5.0}]
    resources.genome_repo.get_top_tags_for_movies.return_value = []

    top_theme, _top_5, _insights = _analyze_themes_from_ratings(resources, "user123", all_ratings)

    assert top_theme is None


def test_watchlist_metrics_empty():
    """Test empty watchlist metrics."""
    resources = Mock()
    resources.watchlist_repo.get_by_user.return_value = []
    resources.ratings_repo.get_by_user.return_value = []

    metrics = _analyze_watchlist_metrics(resources, "user123")

    assert metrics.total_watchlist_items == 0
    assert metrics.completion_rate == 0.0


def test_watchlist_metrics_all_rated():
    """Test watchlist with all items rated."""
    resources = Mock()
    resources.watchlist_repo.get_by_user.return_value = [
        {"movie_id": 1, "added_at": "2024-01-01T00:00:00Z"},
        {"movie_id": 2, "added_at": "2024-01-02T00:00:00Z"},
    ]
    resources.ratings_repo.get_by_user.return_value = [
        {"movie_id": 1, "rating": 5.0, "timestamp": "2024-01-01T01:00:00Z"},
        {"movie_id": 2, "rating": 4.0, "timestamp": "2024-01-02T02:00:00Z"},
    ]
    resources.movies_repo.get_by_id.return_value = {"genres": ["Action"]}

    metrics = _analyze_watchlist_metrics(resources, "user123")

    assert metrics.completion_rate == 100.0
    assert metrics.average_rating == 4.5


def test_generate_insights_with_ratings():
    """Test insights generation with ratings."""
    resources = Mock()
    resources.users_repo.get_by_id.return_value = {"id": "user123"}
    resources.ratings_repo.get_by_user.return_value = [
        {"movie_id": 1, "rating": 5.0},
        {"movie_id": 2, "rating": 4.0},
    ]
    resources.watchlist_repo.get_by_user.return_value = []
    resources.movies_repo.get_by_id.return_value = {"genres": ["Action"]}
    resources.genome_repo.get_top_tags_for_movies.return_value = []

    insights = generate_user_insights(resources, "user123")

    assert insights is not None
    assert insights.total_ratings == 2


def test_get_summary_success():
    """Test summary generation."""
    resources = Mock()
    resources.users_repo.get_by_id.return_value = {"id": "user123"}
    resources.ratings_repo.get_by_user.return_value = [{"movie_id": 1, "rating": 5.0}]
    resources.watchlist_repo.get_by_user.return_value = []
    resources.movies_repo.get_by_id.return_value = {"genres": ["Action"]}
    resources.genome_repo.get_top_tags_for_movies.return_value = []

    summary = get_user_insights_summary(resources, "user123")

    assert summary is not None
    assert summary.user_id == "user123"


def test_get_summary_user_not_found():
    """Test summary when user not found."""
    resources = Mock()
    resources.users_repo.get_by_id.return_value = None

    summary = get_user_insights_summary(resources, "nonexistent")

    assert summary is None
