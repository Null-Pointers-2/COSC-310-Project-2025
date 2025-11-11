"""Unit tests for ratings service."""
import pytest
from unittest.mock import Mock
from app.services import ratings_service
from app.repositories.ratings_repo import RatingsRepository
from app.schemas.rating import RatingCreate

@pytest.fixture
def setup_repos(tmp_path):
    """Setup temporary repositories for testing."""
    ratings_file = tmp_path / "ratings.json"

    ratings_repo = RatingsRepository(ratings_file=str(ratings_file))

    resources = Mock()
    resources.ratings_repo = ratings_repo

    return resources

def test_create_rating(setup_repos):
    """Test creating a new rating."""
    resources = setup_repos

    rating_data = RatingCreate(movie_id=1, rating=4.0)
    result = ratings_service.create_rating(resources, "u1", rating_data)
    
    assert result.rating == 4.0
    assert result.user_id == "u1"
    assert result.movie_id == 1

    all_ratings = resources.ratings_repo.get_all()
    assert len(all_ratings) == 1

def test_create_duplicate_rating_fails(setup_repos):
    """Test that creating a duplicate rating raises ValueError."""
    resources = setup_repos

    rating_data1 = RatingCreate(movie_id=1, rating=4.0)
    ratings_service.create_rating(resources, "u1", rating_data1)

    rating_data2 = RatingCreate(movie_id=1, rating=5.0)
    with pytest.raises(ValueError, match="Rating already exists"):
        ratings_service.create_rating(resources, "u1", rating_data2)

    all_ratings = resources.ratings_repo.get_all()
    assert len(all_ratings) == 1
    assert all_ratings[0]["rating"] == 4.0

def test_update_existing_rating(setup_repos):
    """Test updating an existing rating."""
    resources = setup_repos

    created = resources.ratings_repo.create({"user_id": "u1", "movie_id": 1, "rating": 4.0})

    from app.schemas.rating import RatingUpdate
    update_data = RatingUpdate(rating=5.0)
    updated = ratings_service.update_rating(resources, created["id"], "u1", update_data)

    assert updated is not None
    assert updated.rating == 5.0

    all_ratings = resources.ratings_repo.get_all()
    assert len(all_ratings) == 1
    assert all_ratings[0]["rating"] == 5.0

def test_get_user_ratings(setup_repos):
    """Test retrieving all ratings for a user."""
    resources = setup_repos

    resources.ratings_repo.create({"user_id": "u1", "movie_id": 1, "rating": 4.0})
    resources.ratings_repo.create({"user_id": "u1", "movie_id": 2, "rating": 5.0})
    resources.ratings_repo.create({"user_id": "u2", "movie_id": 3, "rating": 3.0})

    user_ratings = ratings_service.get_user_ratings(resources, "u1")
    assert len(user_ratings) == 2
    assert all(r.user_id == "u1" for r in user_ratings)

def test_delete_rating(setup_repos):
    """Test deleting a rating."""
    resources = setup_repos

    created = resources.ratings_repo.create({"user_id": "u2", "movie_id": 2, "rating": 3.0})
    deleted = ratings_service.delete_rating(resources, created["id"], "u2")

    assert deleted is True
    assert resources.ratings_repo.get_by_id(created["id"]) is None

def test_delete_rating_permission_denied(setup_repos):
    """Test that users can't delete other users' ratings."""
    resources = setup_repos

    created = resources.ratings_repo.create({"user_id": "u1", "movie_id": 1, "rating": 4.0})
    deleted = ratings_service.delete_rating(resources, created["id"], "u2")

    assert deleted is False
    assert resources.ratings_repo.get_by_id(created["id"]) is not None

def test_admin_can_delete_any_rating(setup_repos):
    """Test that admin can delete any rating."""
    resources = setup_repos

    created = resources.ratings_repo.create({"user_id": "u1", "movie_id": 1, "rating": 4.0})
    deleted = ratings_service.delete_rating(resources, created["id"], "admin_user", is_admin=True)

    assert deleted is True
    assert resources.ratings_repo.get_by_id(created["id"]) is None
