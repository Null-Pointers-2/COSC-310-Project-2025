"""Movie schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List

class Movie(BaseModel):
    """Complete movie schema."""
    movieId: int
    title: str

    average_rating: Optional[float] = None
    imdb_id: Optional[int] = None
    tmdb_id: Optional[int] = None

    year: Optional[int] = None
    genres: Optional[List[str]] = None

class MoviePage(BaseModel):
    """Paginated movie results."""
    movies: List[Movie]
    total: int
    page: int
    page_size: int
    total_pages: int