"""Movie service."""

from math import ceil

from app.schemas.movie import Movie, MoviePage


def get_movies(
    resources, page: int = 1, page_size: int = 20, query: str | None = None, genre: str | None = None
) -> MoviePage:
    """Get paginated list of movies with optional filters."""
    movies_data, total = resources.movies_repo.get_movies(page=page, limit=page_size, query=query, genre=genre)

    total_pages = ceil(total / page_size) if total > 0 else 1

    for m in movies_data:
        m["average_rating"] = resources.movies_repo.get_average_rating(m["movie_id"])

    return MoviePage(
        movies=[Movie(**m) for m in movies_data],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_movie_by_id(resources, movie_id: int) -> Movie | None:
    """Get movie details."""
    try:
        movie_id_int = int(movie_id)
    except ValueError:
        return None

    if movie_id_int <= 0:
        return None

    movie_data = resources.movies_repo.get_by_id(movie_id_int)
    if not movie_data:
        return None

    avg_rating = resources.movies_repo.get_average_rating(movie_id_int)
    movie_data["average_rating"] = avg_rating

    return Movie(**movie_data)


def get_all_genres(resources) -> list[str]:
    """Get list of all genres."""
    return resources.movies_repo.get_genres()


def get_movie_ratings(resources, movie_id: int) -> list[dict]:
    """Get all ratings for a movie."""
    return resources.ratings_repo.get_by_movie(movie_id)
