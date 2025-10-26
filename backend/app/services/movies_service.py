"""Movie service."""
from typing import List, Optional
from app.repositories.movies_repo import MoviesRepository
from app.repositories.ratings_repo import RatingsRepository
from app.schemas.movie import Movie, MoviePage

movies_repo = MoviesRepository()
ratings_repo = RatingsRepository()

def get_movies(page: int = 1, page_size: int = 30) -> MoviePage:
    """Get paginated list of movies."""
    # DONE: Calculate offset, get movies, return MoviePage
    offset = (page - 1) * page_size
    movies = movies_repo.get_all(limit=page_size, offset=offset)

    total = len(movies_repo.movies_df) if movies_repo.movies_df is not None else 0
    total_pages = ceil(total / page_size) if total > 0 else 1

    # Get avg ratings
    for m in movies:
        m["average_rating"] = movies_repo.get_average_rating(m["movieId"])

    return MoviePage(
        movies=[Movie(**m) for m in movies],
        total =total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

def get_movie_by_id(movie_id: str) -> Optional[Movie]:
    """Get movie details."""
    try:
        movie_id = int(movie_id)
    except ValueError:
        return None
    
    movie_data = movies_repo.get_by_id(movie_id)
    if not movie_data:
        return None
    
    avg_rating = movies_repo.get_average_rating(movie_id)
    movie_data["average_rating"] = avg_rating
    
    return Movie(
        movieId=str(movie_data['movieId']),
        title=movie_data['title'],
        genres=movie_data['genres'], 
        average_rating=avg_rating, # DONE: Calculate rating average from user ratings
        imdb_id=None, # NA
        tmdb_id=None # NA
    )

def search_movies(query: str, limit: int = 20) -> List[Movie]:
    """Search movies by title."""
    # DONE: Use movies_repo.search()
    
    results = movies_repo.search(query=query, limit=limit)
    for m in results:
        m["average_rating"] = movies_repo.get_average_rating(m["movieId"])
    return [Movie(**m) for m in results]

def filter_movies(genre: Optional[str] = None, year: Optional[int] = None, limit: int = 20) -> List[Movie]:
    """Filter movies by genre and/or year."""
    # DONE: Apply filters from repo
    
    if gengre:
        results = movies_repo.filter_by_genre(genre=genre, limit=limit)
    else:
        results = movies_repo.get_all(limit=limit)
    
    for m in results:
        m["average_rating"] = movies_repo.get_average_rating(m["movieId"])
    
    # **Open to extension (year filtering)

    return[Movie(**m) for m in results]

def get_all_genres() -> List[str]:
    """Get list of all genres."""
    # DONE: Use movies_repo.get_genres()
    return movies_repo.get_genres()

def get_movie_ratings(movie_id: str) -> List[dict]:
    """Get all ratings for a movie."""
    # DONE: Use ratings_repo.get_by_movie()
    try:
        movie_id = int(movie_id)
    except ValueError:
        return []
    
    ratings = ratings_repo.get_by_movie(movie_id)
    return ratings
