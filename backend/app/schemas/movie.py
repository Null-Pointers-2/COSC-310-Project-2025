"""Movie schemas."""

from pydantic import BaseModel


class Movie(BaseModel):
    """Complete movie schema."""

    movie_id: int
    title: str
    genres: list[str] | None = None
    year: int | None = None

    imdb_id: int | None = None
    tmdb_id: int | None = None
    average_rating: float | None = None


class MoviePage(BaseModel):
    """Paginated movie results."""

    movies: list[Movie]
    total: int
    page: int
    page_size: int
    total_pages: int
