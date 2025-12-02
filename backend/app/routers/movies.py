"""Movie browsing endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_resources
from app.core.resources import SingletonResources
from app.schemas.movie import Movie, MoviePage
from app.services import movies_service

router = APIRouter()


@router.get("", response_model=MoviePage)
def get_movies(
    resources: Annotated[SingletonResources, Depends(get_resources)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Movies per page")] = 20,
    query: str | None = None,
    genre: str | None = None,
):
    """Get list of movies with optional search, filter, and pagination."""
    return movies_service.get_movies(resources, page=page, page_size=page_size, query=query, genre=genre)


@router.get("/genres", response_model=list[str])
def get_genres(resources=Depends(get_resources)):
    """Get all available genres."""
    return movies_service.get_all_genres(resources)


@router.get("/{movie_id}", response_model=Movie)
def get_movie(movie_id: int, resources=Depends(get_resources)):
    """Get detailed movie information."""
    movie = movies_service.get_movie_by_id(resources, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")
    return movie


@router.get("/{movie_id}/ratings")
def get_movie_ratings(movie_id: int, resources=Depends(get_resources)):
    """Get all ratings for a movie."""
    movie = movies_service.get_movie_by_id(resources, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")
    return movies_service.get_movie_ratings(resources, movie_id)
