import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.v1.router import api_router
from src.core.middleware import LoggingMiddleware, RequestIDMiddleware
from src.services.cache.redis import redis_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Manages startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting Six Figure RAG API...")
    
    # Check Redis connection
    if redis_service.ping():
        logger.info("✅ Redis connection established")
    else:
        logger.warning("⚠️ Redis connection failed - caching disabled")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Six Figure RAG API...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A production-ready RAG (Retrieval-Augmented Generation) API with hybrid search, multi-query retrieval, and multi-modal support.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
    contact={
        "name": "Karthik",
        "email": "karthik@example.com",
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Six Figure RAG API",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
