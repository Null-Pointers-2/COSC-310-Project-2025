from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, users, movies, ratings, recommendations, watchlist, admin, export

app = FastAPI(
    title="Movie Recommendations API",
    description="Backend API for personalized movie recommendations using cosine similarity",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://frontend:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (required for Docker)
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

# Include routers
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
    # TODO: Initialize repositories (create files if they don't exist)
    # TODO: Load/precompute similarity matrix for recommendations
    # TODO: Validate data files
    print("🚀 Application starting up...")

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