from fastapi import APIRouter, status, Query
from typing import List
from schemas.item import Item, ItemCreate, ItemUpdate, Movie, MoviePage
from services.items_service import list_items, create_item, delete_item, update_item, list_movies, get_movie_by_id

router = APIRouter(prefix="/items", tags=["items"])
movieRouter = APIRouter(prefix="/movies", tags=["movies"])

@movieRouter.get("", response_model=MoviePage)
def get_movies(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    page_size: int = Query(30, ge=1, le=100, description="Number of movies per page")
):
    return list_movies(page, page_size)

@movieRouter.get("/{movie_id}", response_model=Movie)
def get_movie(movie_id: int):
    return get_movie_by_id(movie_id)

@router.get("", response_model=List[Item])
def get_items():
    return list_items()

#simple post the payload (is the body of the request)
@router.post("", response_model=Item, status_code=201)
def post_item(payload: ItemCreate):
    return create_item(payload)

from services.items_service import list_items, create_item, get_item_by_id

@router.get("/{item_id}", response_model=Item)
def get_item(item_id: str):
    return get_item_by_id(item_id)

## We use put here because we are not creating an entirely new item, ie. we keep id the same
@router.put("/{item_id}", response_model=Item)
def put_item(item_id: str, payload: ItemUpdate):
    return update_item(item_id, payload)


## we put the status there becuase in a delete, we wont have a return so it indicates it happened succesfully
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(item_id: str):
    delete_item(item_id)
    return None
