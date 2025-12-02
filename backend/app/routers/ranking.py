"""Movie ranking endpoints."""

import csv
import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

logger = logging.getLogger(__name__)


UPDATE_FREQUENCY = 0  # Put as 0 for quicker refresh*
NOISE_FILTER = 0.5 # Strictness value in formula
MIN_VOTE_COUNT = 5

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "../../data/ratings.json"
METADATA_PATH = BASE_DIR / "../../data/ml/movies_clean.csv"

popular_movies_cache = {"last_updated": None, "data": []}


def load_titles_from_csv() -> dict[int, str]:
    if not METADATA_PATH.path.exists():
        return {}

    titles = {}
    try:
        with METADATA_PATH.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    m_id = int(row["movie_id"])
                    titles[m_id] = row["title"]
                except (ValueError, KeyError):
                    continue

    except Exception as e:
            logger.exception("Error loading metadata:")
            raise HTTPException(status_code=500, detail="Metadata err") from e


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
    m = all_counts[int(len(all_counts) * NOISE_FILTER)] if len(all_counts) > MIN_VOTE_COUNT else 1

    weighted_movies = []
    for m_id, stats in movie_stats.items():
        v = stats["count"]
        avg_rating = stats["sum"] / v

        if v >= m:
            score = (v / (v + m) * avg_rating) + (m / (v + m) * mean_vote)

            real_title = csv_titles.get(m_id, f"Movie {m_id}")

            weighted_movies.append(
                {
                    "movie_id": m_id,
                    "score": round(score, 2),
                    "vote_count": v,
                    "avg_rating": round(avg_rating, 2),
                    "title": real_title,
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

        popular_movies_cache["data"] = top_movies
        popular_movies_cache["last_updated"] = now

    except Exception as e:
            logger.exception("Error calculating stats:")
            raise HTTPException(status_code=500, detail="Calculation err") from e

    return top_movies
