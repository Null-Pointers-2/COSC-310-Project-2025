"""Repository for movie data operations."""
from pathlib import Path
from typing import List, Optional, Dict, Any, cast
import pandas as pd
import json
from app.core.config import settings
import re
from statistics import mean

class MoviesRepository:
    """Handle movie data from MovieLens CSV files."""

    def __init__(self, movies_dir: Optional[str] = None):
        if movies_dir is None:
            movies_dir = str(settings.STATIC_DIR / "movies")
        self.movies_dir = Path(movies_dir)
        self.movies_df: Optional[pd.DataFrame] = None
        self.links_df: Optional[pd.DataFrame] = None
        self.genome_scores_df: Optional[pd.DataFrame] = None
        self.genome_tags_df: Optional[pd.DataFrame] = None
        self._load_data()

    def _extract_year(self, title: str) -> Optional[int]:
        """Extract year from movie title."""
        match = re.search(r'\((\d{4})\)\s*$', title)
        if match:
            return int(match.group(1))
        return None

    def _load_data(self):
        """Load movie data into pandas DataFrames."""
        movie_path = self.movies_dir / "movies.csv"
        links_path = self.movies_dir / "links.csv"

        if not movie_path.exists():
            self.movies_df = pd.DataFrame(columns=["movieId", "title", "genres", "year"])
            return
        
        self.movies_df = pd.read_csv(movie_path, encoding="utf-8")
        self.movies_df["genres"] = (
            self.movies_df["genres"].fillna("").str.split("|")
        )
        
        self.movies_df["year"] = self.movies_df["title"].apply(self._extract_year)
        
        if links_path.exists():
            self.links_df = pd.read_csv(links_path, encoding="utf-8")
            self.movies_df = pd.merge(
                self.movies_df,
                self.links_df,
                on="movieId",
                how="left"
            )
            self.movies_df["imdbId"] = self.movies_df["imdbId"].astype("Int64")
            self.movies_df["tmdbId"] = self.movies_df["tmdbId"].astype("Int64")

    def get_paginated_movies(self, page: int, page_size: int) -> tuple[List[Dict[str, Any]], int]:
        """Get paginated list of movies and total count."""
        if self.movies_df is None or self.movies_df.empty:
            return [], 0
        
        total = len(self.movies_df)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_df = self.movies_df.iloc[start_idx:end_idx]
        return cast(List[Dict[str, Any]], paginated_df.to_dict(orient="records")), total

    def get_by_id(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Get a single movie by its ID."""
        if self.movies_df is None or self.movies_df.empty:
            return None

        match = self.movies_df[self.movies_df["movieId"] == movie_id]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all movies with pagination."""
        if self.movies_df is None or self.movies_df.empty:
            return []

        sliced = self.movies_df.iloc[offset:offset + limit]
        return cast(List[Dict[str, Any]], sliced.to_dict(orient="records"))

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search movies by title."""
        if self.movies_df is None or self.movies_df.empty:
            return []

        mask = self.movies_df["title"].str.contains(query, case=False, na=False)
        results = self.movies_df[mask].head(limit)
        return cast(List[Dict[str, Any]], results.to_dict(orient="records"))

    def filter_by_genre(self, genre: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Filter movies by genre."""
        if self.movies_df is None or self.movies_df.empty:
            return []

        results = self.movies_df[
            self.movies_df["genres"].apply(lambda g: genre.lower() in [x.lower() for x in g])
        ].head(limit)
        return cast(List[Dict[str, Any]], results.to_dict(orient="records"))

    def get_genres(self) -> List[str]:
        """Get list of all unique genres."""
        if self.movies_df is None or self.movies_df.empty:
            return []
        all_genres = set(
            genre
            for sublist in self.movies_df["genres"]
            for genre in sublist
            if genre
        )
        return sorted(all_genres)

    def get_average_rating(self, movie_id: int, ratings_path: Optional[Path] = None) -> Optional[float]:
        """Calculate average rating for a movie."""
        if ratings_path is None:
            ratings_path = Path(settings.RATINGS_FILE)
        
        if not ratings_path.exists():
            return None

        try:
            with open(ratings_path, "r", encoding="utf-8") as f:
                ratings = json.load(f)
        except json.JSONDecodeError:
            return None
        
        movie_ratings = [
            float(r["rating"])
            for r in ratings
            if r.get("movie_id") == movie_id
        ]

        if not movie_ratings:
            return None
        
        return round(mean(movie_ratings), 2)