"""Movie service."""
from typing import List, Optional
from app.repositories.movies_repo import MoviesRepository
from app.repositories.ratings_repo import RatingsRepository
from app.schemas.movie import Movie, MovieDetail, MoviePage

movies_repo = MoviesRepository()
ratings_repo = RatingsRepository()

def get_movies(page: int = 1, page_size: int = 30) -> MoviePage:
    """Get paginated list of movies."""
    # TODO: Calculate offset, get movies, return MoviePage
    pass

def get_movie_by_id(movie_id: str) -> Optional[MovieDetail]:
    """Get movie details with ratings."""
    # TODO: Get movie, calculate average rating
    pass

def search_movies(query: str, limit: int = 20) -> List[Movie]:
    """Search movies by title."""
    # TODO: Use movies_repo.search()
    pass

def filter_movies(genre: Optional[str] = None, year: Optional[int] = None, limit: int = 20) -> List[Movie]:
    """Filter movies by genre and/or year."""
    # TODO: Apply filters from repo
    pass

def get_all_genres() -> List[str]:
    """Get list of all genres."""
    # TODO: Use movies_repo.get_genres()
    pass

def get_movie_ratings(movie_id: str) -> List[dict]:
    """Get all ratings for a movie."""
    # TODO: Use ratings_repo.get_by_movie()
    pass
