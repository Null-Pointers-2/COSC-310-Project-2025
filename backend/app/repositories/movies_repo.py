"""Repository for movie data operations."""

import json
import re
from pathlib import Path
from statistics import mean
from typing import Any, cast

import pandas as pd

from app.core.config import settings


class MoviesRepository:
    """Handle movie data from MovieLens CSV files."""

    def __init__(self, movies_dir: str | None = None):
        if movies_dir is None:
            movies_dir = str(settings.STATIC_DIR / "movies")
        self.movies_dir = Path(movies_dir)
        self.movies_df: pd.DataFrame | None = None
        self.links_df: pd.DataFrame | None = None
        self._load_data()

    def _extract_year(self, title: str) -> int | None:
        """Extract year from movie title."""
        match = re.search(r"\((\d{4})\)\s*$", title)
        if match:
            return int(match.group(1))
        return None

    def _load_data(self):
        """Load movie data into pandas DataFrames."""
        movie_path = self.movies_dir / "movies.csv"
        links_path = self.movies_dir / "links.csv"

        if not movie_path.exists():
            self.movies_df = pd.DataFrame(columns=["movie_id", "title", "genres", "year"])
            return

        self.movies_df = pd.read_csv(movie_path, encoding="utf-8", quotechar='"', doublequote=True, escapechar=None)
        self.movies_df["genres"] = self.movies_df["genres"].fillna("").str.split("|")

        self.movies_df["title"] = self.movies_df["title"].str.strip()
        self.movies_df["year"] = self.movies_df["title"].apply(self._extract_year)

        if links_path.exists():
            self.links_df = pd.read_csv(links_path, encoding="utf-8")
            self.movies_df = self.movies_df.merge(self.links_df, on="movie_id", how="left")
            self.movies_df["imdb_id"] = self.movies_df["imdb_id"].astype("Int64")
            self.movies_df["tmdb_id"] = self.movies_df["tmdb_id"].astype("Int64")

    def get_paginated_movies(self, page: int, page_size: int) -> tuple[list[dict[str, Any]], int]:
        """Get paginated list of movies and total count."""
        if self.movies_df is None or self.movies_df.empty:
            return [], 0

        sorted_df = self.movies_df.sort_values(by="movie_id")

        total = len(sorted_df)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_df = sorted_df.iloc[start_idx:end_idx]
        return cast("list[dict[str, Any]]", paginated_df.to_dict(orient="records")), total

    def get_by_id(self, movie_id: int) -> dict[str, Any] | None:
        """Get a single movie by its ID."""
        if self.movies_df is None or self.movies_df.empty:
            return None

        match = self.movies_df[self.movies_df["movie_id"] == movie_id]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Get all movies with pagination."""
        if self.movies_df is None or self.movies_df.empty:
            return []

        sorted_df = self.movies_df.sort_values(by="movie_id")
        sliced = sorted_df.iloc[offset : offset + limit]
        return cast("list[dict[str, Any]]", sliced.to_dict(orient="records"))

    def search(self, query: str, limit: int = 20, offset: int = 0) -> list[dict[str, Any]]:
        """Search movies by title using a simple fuzzy approach."""
        if self.movies_df is None or self.movies_df.empty:
            return []

        query_tokens = query.lower().split()

        if not query_tokens:
            return []

        def fuzzy_match(title: str) -> bool:
            title_lower = title.lower()
            return all(token in title_lower for token in query_tokens)

        mask = self.movies_df["title"].apply(fuzzy_match)
        results = self.movies_df[mask].iloc[offset : offset + limit]

        return cast("list[dict[str, Any]]", results.to_dict(orient="records"))

    def filter_by_genre(self, genre: str, limit: int = 20, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
        """Filter movies by genre with pagination."""
        if self.movies_df is None or self.movies_df.empty:
            return [], 0

        mask = self.movies_df["genres"].apply(lambda g: genre.lower() in [x.lower() for x in g])
        filtered_df = self.movies_df[mask]

        total = len(filtered_df)
        sliced = filtered_df.iloc[offset : offset + limit]

        return cast("list[dict[str, Any]]", sliced.to_dict(orient="records")), total

    def get_genres(self) -> list[str]:
        """Get list of all unique genres, excluding unwanted ones."""
        if self.movies_df is None or self.movies_df.empty:
            return []

        all_genres = {genre for sublist in self.movies_df["genres"] for genre in sublist if genre}

        return sorted(all_genres)

    def get_average_rating(self, movie_id: int, ratings_path: Path | None = None) -> float | None:
        """Calculate average rating for a movie."""
        if ratings_path is None:
            ratings_path = Path(settings.RATINGS_FILE)

        if not ratings_path.exists():
            return None

        try:
            with Path.open(ratings_path, encoding="utf-8") as f:
                ratings = json.load(f)
        except json.JSONDecodeError:
            return None

        movie_ratings = [float(r["rating"]) for r in ratings if r.get("movie_id") == movie_id]

        if not movie_ratings:
            return None

        return round(mean(movie_ratings), 2)
