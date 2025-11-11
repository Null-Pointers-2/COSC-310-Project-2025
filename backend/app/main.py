import threading
from typing import Optional

from argon2 import PasswordHasher
from fastapi import FastAPI

from app.repositories.movies_repo import MoviesRepository
from app.repositories.penalties_repo import PenaltiesRepository
from app.repositories.ratings_repo import RatingsRepository
from app.repositories.recommendations_repo import RecommendationsRepository
from app.repositories.users_repo import UsersRepository
from app.repositories.watchlist_repo import WatchlistRepository
from app.routers import (
    admin,
    auth,
    export,
    movies,
    ratings,
    recommendations,
    users,
    watchlist,
)


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

            print("Initializing singleton resources...")
            self.users_repo = UsersRepository()
            self.movies_repo = MoviesRepository()
            self.ratings_repo = RatingsRepository()
            self.watchlist_repo = WatchlistRepository()
            self.recommendations_repo = RecommendationsRepository()
            self.penalties_repo = PenaltiesRepository()

            self.password_hasher = PasswordHasher()

            SingletonResources._initialized = True
            print("Singleton resources initialized successfully")

    def cleanup(self):
        """Cleanup resources on shutdown."""
        print("Cleaning up singleton resources...")
        print("Singleton resources cleaned up")


app = FastAPI(
    title="Movie Recommendations API",
    description="Backend API for personalized movie recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns service status and version information.
    """
    return {
        "status": "healthy",
        "service": "movie-recommendations-backend",
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Movie Recommendations API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(movies.router, prefix="/movies", tags=["Movies"])
app.include_router(ratings.router, prefix="/ratings", tags=["Ratings"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(export.router, prefix="/export", tags=["Export"])


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup.
    Initialize singleton resources and load data.
    """
    print("Application starting up...")
    app.state.resources = SingletonResources()
    # TODO: Load/precompute similarity matrix for recommendations (still not sure how this will work...)
    # TODO: Validate data files
    print("Application startup complete")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown.
    Cleanup resources and save state.
    """
    print("Application shutting down...")
    if hasattr(app.state, "resources") and app.state.resources:
        app.state.resources.cleanup()
    print("Application shutdown complete")
