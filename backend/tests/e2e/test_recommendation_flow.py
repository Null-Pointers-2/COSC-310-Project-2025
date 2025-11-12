"""
End-to-end test for complete recommendation flow.

Tests the entire recommendation pipeline from user registration
through rating movies to receiving personalized recommendations.
"""

from pathlib import Path

import pytest

from app.main import app


def check_ml_artifacts_exist():
    """Check if required ML artifacts exist."""
    ml_dir = Path("data/ml")
    required_files = [
        "movies_clean.csv",
        "similarity_matrix.npy",
        "movie_id_to_idx.json",
    ]
    missing = [f for f in required_files if not (ml_dir / f).exists()]
    return len(missing) == 0, missing


def force_recommender_initialization(app):
    """Force lazy initialization of the recommender if not already initialized."""
    if app.state.resources._recommender is None:
        _ = app.state.resources.recommender


def test_complete_recommendation_flow(client, clean_test_data):
    """
    E2E test for complete recommendation flow.

    Flow:
    1. User registers and authenticates
    2. User browses movies
    3. User rates multiple movies (some high, some low)
    4. User requests recommendations (gets personalized results)
    5. User refreshes recommendations after adding more ratings
    """
    users_repo = clean_test_data["users_repo"]
    ratings_repo = clean_test_data["ratings_repo"]
    recommendations_repo = clean_test_data["recommendations_repo"]

    ml_ready, missing = check_ml_artifacts_exist()
    if not ml_ready:
        pytest.skip(
            f"ML artifacts not found. Run 'python scripts/setup_ml_data.py' first. Missing files: {', '.join(missing)}",
        )

    force_recommender_initialization(app)

    # Step 1: Register and authenticate
    register_response = client.post(
        "/auth/register",
        json={
            "username": "e2e_user",
            "email": "e2e@test.com",
            "password": "E2ETest123!",
        },
    )
    assert register_response.status_code == 201, "User registration should succeed"
    user = register_response.json()
    assert user["username"] == "e2e_user"
    assert user["email"] == "e2e@test.com"

    login_response = client.post("/auth/login", data={"username": "e2e_user", "password": "E2ETest123!"})
    assert login_response.status_code == 200, "Login should succeed"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["id"] == user["id"]

    # Step 2: Browse movies
    movies_response = client.get("/movies?page=1&page_size=30")
    assert movies_response.status_code == 200
    movies_data = movies_response.json()
    assert "movies" in movies_data
    assert len(movies_data["movies"]) > 0
    movies = movies_data["movies"]

    first_movie = movies[0]
    movie_detail_response = client.get(f"/movies/{first_movie['movie_id']}")
    assert movie_detail_response.status_code == 200
    movie_detail = movie_detail_response.json()
    assert movie_detail["movie_id"] == first_movie["movie_id"]

    # Step 3: Rate movies
    rated_movies = []
    high_rated_movies = []
    low_rated_movies = []

    for i, movie in enumerate(movies[:10]):
        rating_value = 4.5 if i < 5 else 2.0

        rating_response = client.post(
            "/ratings",
            headers=headers,
            json={"movie_id": movie["movie_id"], "rating": rating_value},
        )
        assert rating_response.status_code == 201, f"Rating creation should succeed for movie {movie['movie_id']}"
        rating = rating_response.json()
        assert rating["rating"] == rating_value
        assert rating["movie_id"] == movie["movie_id"]

        rated_movies.append(movie["movie_id"])
        if rating_value >= 4.0:
            high_rated_movies.append(movie["movie_id"])
        else:
            low_rated_movies.append(movie["movie_id"])

    my_ratings_response = client.get("/ratings/me", headers=headers)
    assert my_ratings_response.status_code == 200
    my_ratings = my_ratings_response.json()
    assert len(my_ratings) == 10

    # Verify ratings are stored in test repository
    user_ratings_from_repo = ratings_repo.get_by_user(user["id"])
    assert len(user_ratings_from_repo) == 10

    # Step 4: Get recommendations
    recommendations_response = client.get("/recommendations/me?limit=10", headers=headers)
    assert recommendations_response.status_code == 200, (
        f"Recommendations endpoint should succeed. Response: {recommendations_response.text}"
    )
    recommendations_data = recommendations_response.json()
    assert "user_id" in recommendations_data
    assert "recommendations" in recommendations_data
    assert recommendations_data["user_id"] == user["id"]

    recommendations = recommendations_data["recommendations"]

    if len(recommendations) == 0:
        pytest.fail(
            "No recommendations returned. This could mean:\n"
            "1. ML artifacts are corrupted - try running 'python scripts/setup_ml_data.py' again\n"
            "2. The rated movies aren't in the cleaned dataset\n"
            "3. The similarity matrix couldn't find similar movies\n"
            f"Rated movie IDs: {rated_movies}",
        )

    assert len(recommendations) > 0, "Should receive recommendations"
    assert len(recommendations) <= 10, "Should respect limit"

    first_rec = recommendations[0]
    assert "movie_id" in first_rec
    assert "similarity_score" in first_rec
    assert isinstance(first_rec["similarity_score"], (int, float))
    assert 0 <= first_rec["similarity_score"] <= 1

    recommended_movie_ids = {rec["movie_id"] for rec in recommendations}
    rated_movie_ids_set = set(rated_movies)
    overlap = recommended_movie_ids.intersection(rated_movie_ids_set)
    assert len(overlap) == 0, "Recommendations should not include already-rated movies"

    scores = [rec["similarity_score"] for rec in recommendations]
    assert scores == sorted(scores, reverse=True), "Recommendations should be sorted by score"

    # Test caching
    cached_data = recommendations_repo.get_for_user(user["id"])
    assert cached_data is not None, "Recommendations should be cached"
    assert len(cached_data["recommendations"]) > 0

    cached_response = client.get("/recommendations/me?limit=10", headers=headers)
    assert cached_response.status_code == 200
    cached_recommendations = cached_response.json()["recommendations"]

    assert cached_recommendations == recommendations, "Cached recommendations should be identical"

    # Test refresh after adding more ratings
    additional_movies = movies[10:15]  # Next 5 movies
    additional_rated = []

    for movie in additional_movies:
        rating_response = client.post(
            "/ratings",
            headers=headers,
            json={"movie_id": movie["movie_id"], "rating": 4.0},
        )
        assert rating_response.status_code == 201
        additional_rated.append(movie["movie_id"])

    all_rated_movies = rated_movies + additional_rated

    # Verify all ratings are in repository
    all_user_ratings = ratings_repo.get_by_user(user["id"])
    assert len(all_user_ratings) == 15

    refresh_response = client.post("/recommendations/me/refresh?limit=10", headers=headers)
    assert refresh_response.status_code == 200
    refreshed_recommendations = refresh_response.json()["recommendations"]
    assert len(refreshed_recommendations) > 0

    refreshed_movie_ids = {rec["movie_id"] for rec in refreshed_recommendations}
    all_rated_ids_set = set(all_rated_movies)
    overlap_after_refresh = refreshed_movie_ids.intersection(all_rated_ids_set)
    assert len(overlap_after_refresh) == 0, "Refreshed recommendations should exclude all rated movies"

    # Test force refresh
    force_refresh_response = client.get("/recommendations/me?limit=10&force_refresh=true", headers=headers)
    assert force_refresh_response.status_code == 200
    force_refreshed = force_refresh_response.json()["recommendations"]
    assert len(force_refreshed) > 0

    # Test similar movies endpoint
    seed_movie_id = high_rated_movies[0]

    similar_response = client.get(f"/recommendations/similar/{seed_movie_id}?limit=5", headers=headers)

    if similar_response.status_code == 200:
        similar_movies = similar_response.json()
        assert len(similar_movies) > 0
        assert len(similar_movies) <= 5

        for similar in similar_movies:
            assert "movie_id" in similar
            assert "similarity_score" in similar
            assert similar["movie_id"] != seed_movie_id, "Similar movies should not include seed movie"

    # Test dashboard integration
    dashboard_response = client.get("/users/me/dashboard", headers=headers)
    if dashboard_response.status_code == 200:
        dashboard = dashboard_response.json()
        assert "user" in dashboard
        assert "recent_ratings" in dashboard
        assert "recommendations" in dashboard
        assert dashboard["user"]["id"] == user["id"]

    # Test user profile stats
    profile_response = client.get("/users/me", headers=headers)
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["total_ratings"] == len(all_rated_movies)
    assert profile["average_rating"] > 0

    # Verify user exists in test repository
    user_from_repo = users_repo.get_by_id(user["id"])
    assert user_from_repo is not None
    assert user_from_repo["username"] == "e2e_user"
