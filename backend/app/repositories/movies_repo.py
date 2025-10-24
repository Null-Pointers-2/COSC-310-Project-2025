"""Repository for movie data operations."""
from pathlib import Path
from typing import List, Optional, Dict, Any
import pandas as pd

class MoviesRepository:
    """Handle movie data from MovieLens CSV files."""

    def __init__(self, movies_dir: str = "movies"):
        self.movies_dir = Path(movies_dir)
        self.movies_df: Optional[pd.DataFrame] = None
        self.genome_scores_df: Optional[pd.DataFrame] = None
        self.genome_tags_df: Optional[pd.DataFrame] = None
        self._load_data()

    def _load_data(self):
        """Load movie data into pandas DataFrames."""
        movie_path = self.movies_dir / "movie.csv"
        if not movie_path.exists():
            self.movies_df = pd.DataFrame(columns=["movieId", "title", "genres"])
            return
        self.movies_df = pd.read_csv(movie_path, encoding="utf-8")
        self.movies_df["genres"] = self.movies_df["genres"].fillna("").apply(
            lambda x: x.split("|") if x else []
        )

    def get_paginated_movies(self, page: int, page_size: int) -> tuple[List[Dict[str, Any]], int]:
        """Get paginated list of movies and total count."""
        if self.movies_df is None or self.movies_df.empty:
            return [], 0
        
        total = len(self.movies_df)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_df = self.movies_df.iloc[start_idx:end_idx]
        return paginated_df.to_dict(orient="records"), total

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
        return sliced.to_dict(orient="records")

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search movies by title."""
        if self.movies_df is None or self.movies_df.empty:
            return []

        mask = self.movies_df["title"].str.contains(query, case=False, na=False)
        results = self.movies_df[mask].head(limit)
        return results.to_dict(orient="records")

    def filter_by_genre(self, genre: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Filter movies by genre."""
        if self.movies_df is None or self.movies_df.empty:
            return []

        results = self.movies_df[
            self.movies_df["genres"].apply(lambda g: genre.lower() in [x.lower() for x in g])
        ].head(limit)
        return results.to_dict(orient="records")

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

    def get_movie_tags(self, movie_id: int) -> List[Dict[str, Any]]:
        """Get genome tags for a movie (placeholder for now)."""
        # TODO: Implement once genome_scores.csv and genome_tags.csv are loaded
        pass

