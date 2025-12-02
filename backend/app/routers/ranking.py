import csv
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter()

UPDATE_FREQUENCY = 0
NOISE_FILTER = 0.5
DATA_PATH = Path(__file__).parent / "../../data/ratings.json"
METADATA_PATH = Path(__file__).parent / "../../data/ml/movies_clean.csv"
MIN_METRICS_COUNT = 5

popular_movies_cache = {"last_updated": None, "data": []}


def load_titles_from_csv() -> dict[int, Any]:
    if not METADATA_PATH.exists():
        return {}

    titles = {}
    try:
        with METADATA_PATH.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    m_id = int(row["movie_id"])
                    titles[m_id] = {
                        "title": row["title"],
                        "tmdb_id": row.get("tmdb_id"),
                    }
                except (ValueError, KeyError):
                    continue

    except (OSError, csv.Error):
        pass

    return titles


def calculate_weighted_rating(ratings_list: list[dict]) -> list[dict]:
    if not ratings_list:
        return []

    csv_titles = load_titles_from_csv()

    movie_stats = {}

    for r in ratings_list:
        m_id = r["movie_id"]
        val = r["rating"]
        if m_id not in movie_stats:
            movie_stats[m_id] = {"sum": 0.0, "count": 0}
        movie_stats[m_id]["sum"] += val
        movie_stats[m_id]["count"] += 1

    total_rating_sum = sum(r["rating"] for r in ratings_list)
    total_count = len(ratings_list)
    mean_vote = total_rating_sum / total_count if total_count > 0 else 0

    all_counts = sorted([stats["count"] for stats in movie_stats.values()])
    m = all_counts[int(len(all_counts) * NOISE_FILTER)] if len(all_counts) > MIN_METRICS_COUNT else 1

    weighted_movies = []
    for m_id, stats in movie_stats.items():
        v = stats["count"]
        avg_val = stats["sum"] / v

        if v >= m:
            score = (v / (v + m) * avg_val) + (m / (v + m) * mean_vote)

            # Handle testing data as well
            metadata = csv_titles.get(m_id)
            real_title = f"Movie {m_id}"
            tmdb_id = None

            if metadata:
                if isinstance(metadata, str):
                    real_title = metadata
                elif isinstance(metadata, dict):
                    real_title = metadata.get("title", real_title)
                    tmdb_id = metadata.get("tmdb_id")

            weighted_movies.append(
                {
                    "movie_id": m_id,
                    "score": round(score, 2),
                    "vote_count": v,
                    "avg_rating": round(avg_val, 2),
                    "title": real_title,
                    "tmdb_id": tmdb_id,
                }
            )

    weighted_movies.sort(key=lambda x: x["score"], reverse=True)
    return weighted_movies[:5]


@router.get("/ranking/popular")
def get_popular_movies():
    now = datetime.now(UTC)

    if (
        popular_movies_cache["data"]
        and popular_movies_cache["last_updated"]
        and (now - popular_movies_cache["last_updated"]) < timedelta(hours=UPDATE_FREQUENCY)
    ):
        return popular_movies_cache["data"]

    if not DATA_PATH.exists():
        return []

    try:
        with DATA_PATH.open() as f:
            raw_data = json.load(f)

        top_movies = calculate_weighted_rating(raw_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Calculation err") from e

    popular_movies_cache["data"] = top_movies
    popular_movies_cache["last_updated"] = now

    return top_movies
