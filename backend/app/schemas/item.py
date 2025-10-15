from pydantic import BaseModel
from typing import List

class Item(BaseModel):
    id: str
    title: str
    category: str
    tags: List[str] = []

class ItemCreate(BaseModel):
    title: str
    category: str
    tags: List[str] = []

class ItemUpdate(BaseModel):
    title : str
    category:str
    tags: List[str] = []

class Movie(BaseModel):
    movieId: int
    title: str
    genres: List[str] = []

class MoviePage(BaseModel):
    page: int
    page_size: int
    total_movies: int
    total_pages: int
    movies: List[Movie]
