"""Movie schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List

class MovieBase(BaseModel):
    """Base movie schema."""
    movieId: str
    title: str
    genres: Optional[str] = None

class Movie(MovieBase):
    """Complete movie schema."""
    year: Optional[int] = None
    
    class Config:
        from_attributes = True

class MovieDetail(Movie):
    """Detailed movie information with ratings."""
    average_rating: Optional[float] = None
    total_ratings: int = 0
    imdb_id: Optional[str] = None
    tmdb_id: Optional[str] = None

class MoviePage(BaseModel):
    """Paginated movie results."""
    movies: List[Movie]
    total: int
    page: int
    page_size: int
    total_pages: int