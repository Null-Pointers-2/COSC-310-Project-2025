"""Movie service."""
from typing import List, Optional
from math import ceil
from app.repositories.movies_repo import MoviesRepository
from app.repositories.ratings_repo import RatingsRepository
from app.schemas.movie import Movie, MoviePage

movies_repo = MoviesRepository()
ratings_repo = RatingsRepository()

def get_movies(page: int = 1, page_size: int = 30) -> MoviePage:
    """Get paginated list of movies."""
    offset = (page - 1) * page_size
    movies = movies_repo.get_all(limit=page_size, offset=offset)

    total = len(movies_repo.movies_df) if movies_repo.movies_df is not None else 0
    total_pages = ceil(total / page_size) if total > 0 else 1

    for m in movies:
        m["average_rating"] = movies_repo.get_average_rating(m["movieId"])

    return MoviePage(
        movies=[Movie(**m) for m in movies],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

def get_movie_by_id(movie_id: int) -> Optional[Movie]:
    """Get movie details."""
    try:
        movie_id_int = int(movie_id)
    except ValueError:
        return None
    
    movie_data = movies_repo.get_by_id(movie_id_int)
    if not movie_data:
        return None
    
    avg_rating = movies_repo.get_average_rating(movie_id_int)
    movie_data["average_rating"] = avg_rating
    
    return Movie(**movie_data)

def search_movies(query: str, limit: int = 20) -> List[Movie]:
    """Search movies by title."""
    results = movies_repo.search(query=query, limit=limit)
    for m in results:
        m["average_rating"] = movies_repo.get_average_rating(m["movieId"])
    return [Movie(**m) for m in results]

def filter_movies(genre: Optional[str] = None, limit: int = 20) -> List[Movie]:
    """Filter movies by genre."""
    if genre:
        results = movies_repo.filter_by_genre(genre=genre, limit=limit)
    else:
        results = movies_repo.get_all(limit=limit)
    
    for m in results:
        m["average_rating"] = movies_repo.get_average_rating(m["movieId"])
    
    return [Movie(**m) for m in results]

def get_all_genres() -> List[str]:
    """Get list of all genres."""
    return movies_repo.get_genres()

def get_movie_ratings(movie_id: int) -> List[dict]:
    """Get all ratings for a movie."""
    ratings = ratings_repo.get_by_movie(movie_id)
    return ratings