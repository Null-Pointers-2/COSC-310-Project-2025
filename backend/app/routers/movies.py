"""Movie browsing endpoints."""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.schemas.movie import Movie, MoviePage
from app.services import movies_service

router = APIRouter()

@router.get("", response_model=MoviePage)
def get_movies(page: int = Query(1, ge=1, description="Page number"), page_size: int = Query(30, ge=1, le=100, description="Movies per page")):
    """Get paginated list of movies."""
    return movies_service.get_movies(page=page, page_size=page_size)

@router.get("/search", response_model=List[Movie])
def search_movies(query: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    """Search movies by title."""
    return movies_service.search_movies(query=query, limit=limit)

@router.get("/filter", response_model=List[Movie])
def filter_movies(genre: Optional[str] = None, limit: int = Query(20, ge=1, le=100)):
    """Filter movies by genre."""
    return movies_service.filter_movies(genre=genre, limit=limit)

@router.get("/genres", response_model=List[str])
def get_genres():
    """Get all available genres."""
    return movies_service.get_all_genres()

@router.get("/{movie_id}", response_model=Movie)
def get_movie(movie_id: int):
    """Get detailed movie information."""
    movie = movies_service.get_movie_by_id(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")
    return movie

@router.get("/{movie_id}/ratings")
def get_movie_ratings(movie_id: int):
    """Get all ratings for a movie."""
    movie = movies_service.get_movie_by_id(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")
    return movies_service.get_movie_ratings(movie_id)