# Claude said:
# Caching is used here because the CSV has 27,000+ movies. Without caching, every API request
# would re-read the entire file from disk and parse all rows, which is inefficient. By loading
# the CSV once into a dictionary indexed by movieId, we get O(1) lookups instead of O(n) linear
# searches, and avoid repeated disk I/O. The cache persists for the lifetime of the application,
# so subsequent requests are nearly instantaneous. The trade-off is ~5-10MB of RAM, which is
# negligible compared to the performance gain.

from pathlib import Path
import csv
from typing import List, Dict, Any, Optional
from functools import lru_cache

MOVIES_CSV_PATH = Path(__file__).resolve().parents[2] / "movies" / "movie.csv"

_movies_cache: Optional[Dict[int, Dict[str, Any]]] = None

def _load_movies_into_cache() -> Dict[int, Dict[str, Any]]:
    global _movies_cache
    if _movies_cache is not None:
        return _movies_cache

    if not MOVIES_CSV_PATH.exists():
        _movies_cache = {}
        return _movies_cache

    movies_dict = {}
    with MOVIES_CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie_id = int(row["movieId"])
            movies_dict[movie_id] = {
                "movieId": movie_id,
                "title": row["title"],
                "genres": row["genres"].split("|") if row["genres"] else []
            }
    _movies_cache = movies_dict
    return _movies_cache

def get_paginated_movies(page: int, page_size: int) -> tuple[List[Dict[str, Any]], int]:
    movies_dict = _load_movies_into_cache()
    all_movies = list(movies_dict.values())
    total = len(all_movies)

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    return all_movies[start_idx:end_idx], total

def get_movie_by_id(movie_id: int) -> Optional[Dict[str, Any]]:
    movies_dict = _load_movies_into_cache()
    return movies_dict.get(movie_id)
