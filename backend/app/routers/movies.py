"""Movie browsing endpoints."""
from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from app.schemas.movie import Movie, MovieDetail, MoviePage
from app.services import movies_service

router = APIRouter()

@router.get("", response_model=MoviePage)
def get_movies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(30, ge=1, le=100, description="Movies per page")
):
    """Get paginated list of movies."""
    # TODO: Call movies_service.get_movies()
    pass

@router.get("/search", response_model=List[Movie])
def search_movies(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Search movies by title."""
    # TODO: Call movies_service.search_movies()
    pass

@router.get("/filter", response_model=List[Movie])
def filter_movies(
    genre: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """Filter movies by genre and/or year."""
    # TODO: Call movies_service.filter_movies()
    pass

@router.get("/genres", response_model=List[str])
def get_genres():
    """Get all available genres."""
    # TODO: Call movies_service.get_all_genres()
    pass

@router.get("/{movie_id}", response_model=MovieDetail)
def get_movie(
    movie_id: str
):
    """Get detailed movie information."""
    # TODO: Call movies_service.get_movie_by_id()
    pass

@router.get("/{movie_id}/ratings")
def get_movie_ratings(
    movie_id: str
):
    """Get all ratings for a movie."""
    # TODO: Call movies_service.get_movie_ratings()
    pass