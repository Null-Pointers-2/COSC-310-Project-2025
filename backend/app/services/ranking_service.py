import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.core.config import settings
from app.core.resources import SingletonResources

# Settings
UPDATE_FREQUENCY_HOURS = 24
NOISE_FILTER = 0.5
MIN_METRICS_COUNT = 5

_popular_cache = {"last_updated": None, "data": []}


def get_popular_movies(resources: SingletonResources) -> list[dict]:
    now = datetime.now(UTC)

    if (
        _popular_cache["data"]
        and _popular_cache["last_updated"]
        and (now - _popular_cache["last_updated"]) < timedelta(hours=UPDATE_FREQUENCY_HOURS)
    ):
        return _popular_cache["data"]

    top_movies = _calculate_weighted_ratings(resources)
    _popular_cache["data"] = top_movies
    _popular_cache["last_updated"] = now
    return top_movies


def _calculate_weighted_ratings(resources: SingletonResources) -> list[dict]:
    ratings_path = Path(settings.RATINGS_FILE)
    if not ratings_path.exists():
        return []

    with ratings_path.open() as f:
        ratings_list = json.load(f)

    if not ratings_list:
        return []

    movie_stats = {}
    total_rating_sum = 0
    for r in ratings_list:
        m_id = r["movie_id"]
        val = float(r["rating"])
        if m_id not in movie_stats:
            movie_stats[m_id] = {"sum": 0.0, "count": 0}
        movie_stats[m_id]["sum"] += val
        movie_stats[m_id]["count"] += 1
        total_rating_sum += val

    total_count = len(ratings_list)
    mean_vote = total_rating_sum / total_count if total_count > 0 else 0

    all_counts = sorted([s["count"] for s in movie_stats.values()])
    m = 1
    if len(all_counts) > MIN_METRICS_COUNT:
        m = all_counts[int(len(all_counts) * NOISE_FILTER)]

    weighted_movies = []
    movies_repo = resources.movies_repo

    for m_id, stats in movie_stats.items():
        v = stats["count"]
        if v < m:
            continue

        avg_val = stats["sum"] / v
        score = (v / (v + m) * avg_val) + (m / (v + m) * mean_vote)

        movie_details = movies_repo.get_by_id(m_id)

        title = f"Movie {m_id}"
        tmdb_id = None

        if movie_details:
            title = movie_details.get("title", title)
            tmdb_id = movie_details.get("tmdb_id")

        weighted_movies.append(
            {
                "movie_id": m_id,
                "score": round(score, 2),
                "vote_count": v,
                "avg_rating": round(avg_val, 2),
                "title": title,
                "tmdb_id": tmdb_id,
            }
        )

    weighted_movies.sort(key=lambda x: x["score"], reverse=True)
    return weighted_movies[:5]
