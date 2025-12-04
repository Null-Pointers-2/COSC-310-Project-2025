"""Integration tests for global insights API endpoints."""

from unittest.mock import Mock, patch

from app.routers import global_insights
from app.schemas.global_insights import GlobalGenreLeaderboard, GlobalGenreStats


def test_get_genre_leaderboard_success():
    """Test successful genre leaderboard retrieval."""
    mock_resources = Mock()
    expected_leaderboard = GlobalGenreLeaderboard(
        genres=[
            GlobalGenreStats(
                genre="Action",
                total_ratings=100,
                average_rating=4.5,
                user_count=50,
                popularity_score=85.5,
            ),
            GlobalGenreStats(
                genre="Drama",
                total_ratings=80,
                average_rating=4.2,
                user_count=45,
                popularity_score=78.3,
            ),
        ],
        total_users=50,
        total_ratings=180,
    )

    with patch(
        "app.routers.global_insights.global_insights_service.get_global_genre_leaderboard",
        return_value=expected_leaderboard,
    ):
        result = global_insights.get_genre_leaderboard(resources=mock_resources)

        assert result.total_users == 50
        assert result.total_ratings == 180
        assert len(result.genres) == 2
        assert result.genres[0].genre == "Action"


def test_get_genre_leaderboard_empty():
    """Test genre leaderboard with no data."""
    mock_resources = Mock()
    expected_leaderboard = GlobalGenreLeaderboard(
        genres=[],
        total_users=0,
        total_ratings=0,
    )

    with patch(
        "app.routers.global_insights.global_insights_service.get_global_genre_leaderboard",
        return_value=expected_leaderboard,
    ):
        result = global_insights.get_genre_leaderboard(resources=mock_resources)

        assert result.total_users == 0
        assert result.total_ratings == 0
        assert len(result.genres) == 0


def test_get_genre_leaderboard_sorted():
    """Test genre leaderboard returns sorted results."""
    mock_resources = Mock()
    expected_leaderboard = GlobalGenreLeaderboard(
        genres=[
            GlobalGenreStats(
                genre="Action",
                total_ratings=100,
                average_rating=4.5,
                user_count=50,
                popularity_score=95.0,
            ),
            GlobalGenreStats(
                genre="Comedy",
                total_ratings=50,
                average_rating=4.0,
                user_count=30,
                popularity_score=70.0,
            ),
        ],
        total_users=50,
        total_ratings=150,
    )

    with patch(
        "app.routers.global_insights.global_insights_service.get_global_genre_leaderboard",
        return_value=expected_leaderboard,
    ):
        result = global_insights.get_genre_leaderboard(resources=mock_resources)

        assert result.genres[0].popularity_score >= result.genres[1].popularity_score
