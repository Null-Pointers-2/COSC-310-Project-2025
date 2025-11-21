"""Main application entry point for the Movie Recommendations API."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.resources import SingletonResources
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

logger = logging.getLogger(__name__)

VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Initializes and cleans up singleton resources.
    """
    logger.info("Application starting up...")

    if not hasattr(app.state, "resources") or app.state.resources is None:
        logger.info("Initializing new SingletonResources...")
        app.state.resources = SingletonResources()
    else:
        logger.info("SingletonResources already initialized, skipping...")

    logger.info("Application startup complete")
    try:
        yield
    finally:
        logger.info("Application shutting down...")
        if hasattr(app.state, "resources") and app.state.resources:
            app.state.resources.cleanup()
        logger.info("Application shutdown complete")


app = FastAPI(
    title="Movie Recommendations API",
    description="Backend API for personalized movie recommendations",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns service status and version information.
    """
    return {
        "status": "healthy",
        "service": "movie-recommendations-backend",
        "version": VERSION,
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Movie Recommendations API",
        "version": VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(movies.router, prefix="/movies", tags=["Movies"])
app.include_router(ratings.router, prefix="/ratings", tags=["Ratings"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(export.router, prefix="/export", tags=["Export"])
