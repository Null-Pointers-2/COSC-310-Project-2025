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

    def get_movies(
        self, page: int = 1, limit: int = 20, query: str | None = None, genre: str | None = None
    ) -> tuple[list[dict[str, Any]], int]:
        """Get movies with optional search and genre filtering."""
        if self.movies_df is None or self.movies_df.empty:
            return [], 0

        df = self.movies_df

        if genre and genre.lower() != "all":
            mask = df["genres"].apply(lambda g: genre.lower() in [x.lower() for x in g])
            df = df[mask]

        if query:
            query_tokens = query.lower().split()

            def fuzzy_match(title: str) -> bool:
                title_lower = title.lower()
                return all(token in title_lower for token in query_tokens)

            mask = df["title"].apply(fuzzy_match)
            df = df[mask]

        df = df.sort_values(by="movie_id")

        total = len(df)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_df = df.iloc[start_idx:end_idx]

        paginated_df = paginated_df.replace({float("nan"): None})

        return cast("list[dict[str, Any]]", paginated_df.to_dict(orient="records")), total

    def get_by_id(self, movie_id: int) -> dict[str, Any] | None:
        """Get a single movie by its ID."""
        if self.movies_df is None or self.movies_df.empty:
            return None

        match = self.movies_df[self.movies_df["movie_id"] == movie_id]
        if match.empty:
            return None

        result = match.iloc[0].replace({float("nan"): None})
        return result.to_dict()

    def get_genres(self) -> list[str]:
        """Get list of all unique genres."""
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
