"""Recommendations service using cosine similarity."""
from typing import List
from app.repositories.ratings_repo import RatingsRepository
from app.repositories.recommendations_repo import RecommendationsRepository
from app.repositories.movies_repo import MoviesRepository
from app.schemas.recommendation import RecommendationList, RecommendationItem

ratings_repo = RatingsRepository()
recommendations_repo = RecommendationsRepository()
movies_repo = MoviesRepository()

def get_recommendations(user_id: str, limit: int = 10, force_refresh: bool = False) -> RecommendationList:
    """Get personalized recommendations for a user."""
    # TODO: Check if cached recommendations exist and are fresh
    # If yes and not force_refresh, return cached
    # If no or force_refresh, generate new recommendations
    pass

def generate_recommendations(user_id: str, limit: int = 10) -> List[RecommendationItem]:
    """Generate new recommendations using cosine similarity."""
    # TODO (notes for future Evan): 
    # 1. Get user's ratings
    # 2. Get user's highest-rated movies
    # 3. Use recommender.get_similar_movies() for each
    # 4. Aggregate and rank results
    # 5. Filter out already-rated movies
    # 6. Return top N recommendations
    pass

def get_similar_movies(movie_id: str, limit: int = 10) -> List[RecommendationItem]:
    """Get movies similar to a given movie."""
    # TODO: Use recommender.get_similar_movies()
    pass