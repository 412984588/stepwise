# Backend Dockerfile for StepWise (Python/FastAPI)
FROM python:3.11-slim

# Set working directory to project root
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependency files first (for better caching)
COPY backend/pyproject.toml ./backend/

# Install Python dependencies
WORKDIR /app/backend
RUN pip install --no-cache-dir -e .

# Back to project root
WORKDIR /app

# Copy backend application code
COPY backend ./backend

# Create data directory for SQLite
RUN mkdir -p /data

# Set DATABASE_URL
ENV DATABASE_URL="sqlite:////data/stepwise.db"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app /data
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Run the application from project root
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
