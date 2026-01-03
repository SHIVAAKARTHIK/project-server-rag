# =============================================================================
# Six Figure RAG - Unified Dockerfile
# =============================================================================
# Single image for both API and Celery worker
# =============================================================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies for document processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    libmagic1 \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package installer)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN UV_HTTP_TIMEOUT=300 uv pip install --system --no-cache -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check (using Python instead of curl since we switch to non-root user)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Default command (overridden in docker-compose for celery)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]