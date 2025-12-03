"""Repository for genome tags and scores data."""

from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config import settings


class GenomeRepository:
    """Handle genome tags and scores from MovieLens dataset."""

    def __init__(self, genome_tags_path: str | None = None, genome_scores_path: str | None = None):
        if genome_tags_path is None:
            genome_tags_path = settings.GENOME_TAGS_CSV
        if genome_scores_path is None:
            genome_scores_path = settings.GENOME_SCORES_CSV

        self.genome_tags_path = Path(genome_tags_path)
        self.genome_scores_path = Path(genome_scores_path)

        self.tags_df: pd.DataFrame | None = None
        self.scores_df: pd.DataFrame | None = None
        self._load_data()

    def _load_data(self):
        """Load genome data into pandas DataFrames."""
        # Load tags (small file - ~1k rows)
        if self.genome_tags_path.exists():
            self.tags_df = pd.read_csv(self.genome_tags_path, encoding="utf-8")
        else:
            self.tags_df = pd.DataFrame(columns=["tag_id", "tag"])

        # Load all scores into memory for fast lookups (~500MB RAM)
        # This matches what the ML recommender does for performance
        if self.genome_scores_path.exists():
            self.scores_df = pd.read_csv(self.genome_scores_path, encoding="utf-8")
        else:
            self.scores_df = pd.DataFrame(columns=["movie_id", "tag_id", "relevance"])

    def get_tag_name(self, tag_id: int) -> str | None:
        """Get tag name by tag_id."""
        if self.tags_df is None or self.tags_df.empty:
            return None

        match = self.tags_df[self.tags_df["tag_id"] == tag_id]
        if match.empty:
            return None

        return str(match.iloc[0]["tag"])

    def get_tag_id(self, tag_name: str) -> int | None:
        """Get tag_id by tag name."""
        if self.tags_df is None or self.tags_df.empty:
            return None

        match = self.tags_df[self.tags_df["tag"].str.lower() == tag_name.lower()]
        if match.empty:
            return None

        return int(match.iloc[0]["tag_id"])

    def get_all_tags(self) -> list[dict[str, Any]]:
        """Get all tags."""
        if self.tags_df is None or self.tags_df.empty:
            return []

        return self.tags_df.to_dict(orient="records")  # type: ignore[return-value]

    def get_movie_tags(self, movie_id: int, min_relevance: float = 0.5) -> list[dict[str, Any]]:
        """
        Get tags for a specific movie with relevance >= threshold.

        Args:
            movie_id: The movie ID
            min_relevance: Minimum relevance score (0-1), default 0.5

        Returns:
            List of dicts with tag_id, tag_name, and relevance
        """
        if not self.genome_scores_path.exists():
            return []

        # Load scores for this specific movie (chunked reading for efficiency)
        chunks = []
        for chunk in pd.read_csv(
            self.genome_scores_path, encoding="utf-8", chunksize=100000, usecols=["movie_id", "tag_id", "relevance"]
        ):
            movie_chunk = chunk[chunk["movie_id"] == movie_id]
            if not movie_chunk.empty:
                chunks.append(movie_chunk)

        if not chunks:
            return []

        movie_scores = pd.concat(chunks)
        movie_scores = movie_scores[movie_scores["relevance"] >= min_relevance]

        if movie_scores.empty:
            return []

        # Join with tag names
        if self.tags_df is not None:
            movie_scores = movie_scores.merge(self.tags_df, on="tag_id", how="left")

        movie_scores = movie_scores.sort_values("relevance", ascending=False)

        return movie_scores.to_dict(orient="records")  # type: ignore[return-value]

    def get_top_tags_for_movies(
        self, movie_ids: list[int], top_n: int = 10, min_relevance: float = 0.5
    ) -> list[dict[str, Any]]:
        """
        Get top tags across multiple movies.

        Args:
            movie_ids: List of movie IDs
            top_n: Number of top tags to return
            min_relevance: Minimum relevance threshold

        Returns:
            List of dicts with tag_id, tag, avg_relevance, movie_count
        """
        if self.scores_df is None or self.scores_df.empty or not movie_ids:
            return []

        # Filter preloaded scores for these movies (FAST - in-memory lookup)
        scores = self.scores_df[self.scores_df["movie_id"].isin(movie_ids)].copy()
        scores = scores[scores["relevance"] >= min_relevance]

        if scores.empty:
            return []

        # Aggregate by tag_id
        tag_stats = scores.groupby("tag_id").agg({"relevance": ["mean", "count"], "movie_id": "nunique"}).reset_index()

        tag_stats.columns = ["tag_id", "avg_relevance", "total_count", "movie_count"]

        # Join with tag names
        if self.tags_df is not None:
            tag_stats = tag_stats.merge(self.tags_df, on="tag_id", how="left")

        # Sort by average relevance and movie count
        tag_stats["score"] = tag_stats["avg_relevance"] * tag_stats["movie_count"]
        tag_stats = tag_stats.sort_values("score", ascending=False).head(top_n)

        return tag_stats[["tag_id", "tag", "avg_relevance", "movie_count"]].to_dict(orient="records")  # type: ignore[return-value]
