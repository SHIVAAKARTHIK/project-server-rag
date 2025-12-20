from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    PROJECT_NAME: str = "Six Figure RAG"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = False
    DOMAIN: str = "http://localhost:3000"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    @property
    def cors_origins(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(",")
    
    # Supabase
    SUPABASE_API_URL: str
    SUPABASE_SERVICE_KEY: str
    
    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str
    
    # LLM & Embeddings
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    DEFAULT_LLM_MODEL: str = "gpt-4-turbo"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-large"
    EMBEDDING_DIMENSIONS: int = 1536
    
    # Clerk Authentication
    CLERK_SECRET_KEY: str
    CLERK_WEBHOOK_SECRET: str
    
    # ScrapingBee (for URL processing)
    SCRAPINGBEE_API_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings() # type: ignore


settings = get_settings()
