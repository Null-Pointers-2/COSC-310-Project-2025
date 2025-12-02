"""Movie ranking endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
import json
import csv
import os
from datetime import datetime, timedelta

router = APIRouter()

UPDATE_FREQUENCY = 0  # Put as 0 for quicker refresh*
NOISE_FILTER = 0.5
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/ratings.json")
METADATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/ml/movies_clean.csv")

popular_movies_cache = {"last_updated": None, "data": []}


def load_titles_from_csv() -> Dict[int, str]:
    if not os.path.exists(METADATA_PATH):
        print(f"Metadata err")
        return {}

    titles = {}
    try:
        with open(METADATA_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    m_id = int(row["movie_id"])
                    titles[m_id] = row["title"]
                except (ValueError, KeyError):
                    continue

    except Exception as e:
        print(f"Metadata err: {e}")

    return titles


def calculate_weighted_rating(ratings_list: List[dict]) -> List[dict]:
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
    C = total_rating_sum / total_count if total_count > 0 else 0

    all_counts = sorted([stats["count"] for stats in movie_stats.values()])
    m = all_counts[int(len(all_counts) * NOISE_FILTER)] if len(all_counts) > 5 else 1

    weighted_movies = []
    for m_id, stats in movie_stats.items():
        v = stats["count"]
        R = stats["sum"] / v

        if v >= m:
            score = (v / (v + m) * R) + (m / (v + m) * C)

            real_title = csv_titles.get(m_id, f"Movie {m_id}")

            weighted_movies.append(
                {
                    "movie_id": m_id,
                    "score": round(score, 2),
                    "vote_count": v,
                    "avg_rating": round(R, 2),
                    "title": real_title,
                }
            )

    weighted_movies.sort(key=lambda x: x["score"], reverse=True)
    return weighted_movies[:5]


@router.get("/ranking/popular")
def get_popular_movies():
    global popular_movies_cache

    now = datetime.now()

    if (
        popular_movies_cache["data"]
        and popular_movies_cache["last_updated"]
        and (now - popular_movies_cache["last_updated"]) < timedelta(hours=UPDATE_FREQUENCY)
    ):
        return popular_movies_cache["data"]

    if not os.path.exists(DATA_PATH):
        return []

    try:
        with open(DATA_PATH, "r") as f:
            raw_data = json.load(f)

        top_movies = calculate_weighted_rating(raw_data)

        popular_movies_cache["data"] = top_movies
        popular_movies_cache["last_updated"] = now

        return top_movies

    except Exception as e:
        print(f"Calculation err: {e}")
        raise HTTPException(status_code=500, detail="Calculation err")
