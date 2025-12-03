"""Integration tests for user insights API endpoints."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.routers import user_insights
from app.schemas.user_insights import UserInsights, UserInsightsSummary, WatchlistMetrics


@pytest.fixture
def mock_resources():
    return Mock()


@pytest.fixture
def mock_user():
    return {"id": "user123", "username": "testuser", "role": "user"}


@pytest.fixture
def sample_insights():
    return UserInsights(
        user_id="user123",
        generated_at=datetime.now(UTC),
        top_genre="Action",
        top_3_genres=["Action", "Drama", "Comedy"],
        genre_insights=[],
        top_theme="original",
        top_5_themes=["original", "great", "good", "story", "fun"],
        theme_insights=[],
        watchlist_metrics=WatchlistMetrics(
            total_watchlist_items=10,
            items_rated=7,
            items_not_rated=3,
            completion_rate=70.0,
            average_rating=4.2,
            average_time_to_rate_hours=24.5,
            genres_in_watchlist=["Action", "Drama"],
            most_common_watchlist_genre="Action",
        ),
        total_ratings=25,
        average_rating=4.1,
        rating_consistency=0.8,
    )


def test_get_insights_success(mock_resources, mock_user, sample_insights):
    with patch(
        "app.routers.user_insights.user_insights_service.generate_user_insights",
        return_value=sample_insights,
    ):
        result = user_insights.get_my_insights(force_refresh=False, current_user=mock_user, resources=mock_resources)

        assert result.user_id == "user123"
        assert result.top_genre == "Action"
        assert result.total_ratings == 25


def test_get_insights_not_found(mock_resources, mock_user):
    with patch("app.routers.user_insights.user_insights_service.generate_user_insights", return_value=None):
        with pytest.raises(HTTPException) as exc:
            user_insights.get_my_insights(force_refresh=False, current_user=mock_user, resources=mock_resources)

        assert exc.value.status_code == 404


def test_get_summary_success(mock_resources, mock_user):
    summary = UserInsightsSummary(
        user_id="user123",
        top_genre="Action",
        top_3_genres=["Action", "Drama", "Comedy"],
        top_theme="original",
        top_5_themes=["original", "great", "good", "story", "fun"],
        watchlist_completion_rate=70.0,
        total_ratings=25,
        generated_at=datetime.now(UTC),
    )

    with patch(
        "app.routers.user_insights.user_insights_service.get_user_insights_summary",
        return_value=summary,
    ):
        result = user_insights.get_my_insights_summary(current_user=mock_user, resources=mock_resources)

        assert result.user_id == "user123"
        assert len(result.top_3_genres) == 3
        assert len(result.top_5_themes) == 5
