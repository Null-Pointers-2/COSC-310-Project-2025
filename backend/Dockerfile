# backend/Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Application code and static data
COPY app ./app
COPY movies ./movies

# Data directory for mutable files
RUN mkdir -p /app/data && \
    mkdir -p /app/app/data && \
    chown -R appuser:appuser /app

# Initial users.csv template (will be overridden by volume)
COPY data/users.csv /app/data/users.csv
RUN chown appuser:appuser /app/data/users.csv

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check endpoint 
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]