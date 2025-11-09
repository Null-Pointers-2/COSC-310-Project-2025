"""Movie schemas."""
from pydantic import BaseModel
from typing import Optional, List

class Movie(BaseModel):
    """Complete movie schema."""
    movieId: int
    title: str
    genres: Optional[List[str]] = None
    year: Optional[int] = None
    
    imdbId: Optional[int] = None
    tmdbId: Optional[int] = None
    average_rating: Optional[float] = None

class MoviePage(BaseModel):
    """Paginated movie results."""
    movies: List[Movie]
    total: int
    page: int
    page_size: int
    total_pages: int