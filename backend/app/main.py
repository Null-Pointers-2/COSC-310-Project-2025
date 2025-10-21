from fastapi import FastAPI

from app.routers import auth, users, movies, ratings, recommendations, watchlist, admin, export

app = FastAPI(
    title="Movie Recommendations API",
    description="Backend API for personalized movie recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
        "version": "1.0.0"
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
        "health": "/health"
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
    Initialize data files, load ML models, etc.
    """
    # TODO: Initialize repositories 
    # TODO: Load/precompute similarity matrix for recommendations (still not sure how this will work...)
    # TODO: Validate data files
    print("Application starting up...")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown.
    Cleanup, save state, etc.
    """
    # TODO: Save any cached data
    # TODO: Cleanup resources
    print("Application shutting down...")