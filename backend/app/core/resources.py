import logging
import threading
from typing import Optional

from argon2 import PasswordHasher

from app.ml.recommender import MovieRecommender
from app.repositories.movies_repo import MoviesRepository
from app.repositories.penalties_repo import PenaltiesRepository
from app.repositories.ratings_repo import RatingsRepository
from app.repositories.recommendations_repo import RecommendationsRepository
from app.repositories.users_repo import UsersRepository
from app.repositories.watchlist_repo import WatchlistRepository

logger = logging.getLogger(__name__)


class SingletonResources:
    """
    Singleton container for shared application resources.
    Initialized once at startup and shared across the application.
    """

    _instance: Optional["SingletonResources"] = None
    _initialized: bool = False
    _lock: threading.Lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        with SingletonResources._lock:
            if SingletonResources._initialized:
                return

            logger.info("Initializing singleton resources...")
            self.users_repo = UsersRepository()
            self.movies_repo = MoviesRepository()
            self.ratings_repo = RatingsRepository()
            self.watchlist_repo = WatchlistRepository()
            self.recommendations_repo = RecommendationsRepository()
            self.penalties_repo = PenaltiesRepository()

            self.password_hasher = PasswordHasher()

            self._recommender = None

            SingletonResources._initialized = True
            logger.info("Singleton resources initialized successfully")

    @property
    def recommender(self):
        if self._recommender is None:
            logger.info("Initializing MovieRecommender...")
            self._recommender = MovieRecommender()
        return self._recommender

    def cleanup(self):
        logger.info("Cleaning up singleton resources...")
        # TODO: Add cleanup logic for repositories/recommender here if needed
        logger.info("Singleton resources cleaned up")
