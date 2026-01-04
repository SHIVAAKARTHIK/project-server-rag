from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Literal
from pydantic import field_validator
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # =========================================================================
    # Application
    # =========================================================================
    PROJECT_NAME: str = "Six Figure RAG"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = False
    DOMAIN: str = "http://localhost:3000"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    @property
    def cors_origins(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(",")
    
    # =========================================================================
    # Supabase
    # =========================================================================
    SUPABASE_API_URL: str
    SUPABASE_SERVICE_KEY: str
    
    @field_validator("SUPABASE_API_URL")
    @classmethod
    def fix_docker_internal_url(cls, v: str) -> str:
        """Replace host.docker.internal with localhost when running outside Docker."""
        is_in_docker = os.path.exists("/.dockerenv")
        if "host.docker.internal" in v and not is_in_docker:
            return v.replace("host.docker.internal", "localhost")
        return v
    
    # =========================================================================
    # Redis & Celery
    # =========================================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # =========================================================================
    # AWS S3
    # =========================================================================
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str
    
    # =========================================================================
    # LLM Provider Selection
    # =========================================================================
    LLM_PROVIDER: Literal["openai", "ollama"] = "openai"
    
    # =========================================================================
    # OpenAI Configuration
    # =========================================================================
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # =========================================================================
    # Ollama Configuration (Local LLM)
    # =========================================================================
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    
    # =========================================================================
    # Embedding Configuration
    # =========================================================================
    EMBEDDING_DIMENSIONS: int = 1536
    
    # =========================================================================
    # Clerk Authentication
    # =========================================================================
    CLERK_SECRET_KEY: str
    CLERK_WEBHOOK_SECRET: str
    
    # =========================================================================
    # ScrapingBee (for URL processing)
    # =========================================================================
    SCRAPINGBEE_API_KEY: str
    # =========================================================================
    # Tavily API key
    # =========================================================================
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # =========================================================================
    # Computed Properties for Active Provider
    # =========================================================================
    @property
    def active_llm_model(self) -> str:
        """Get the active LLM model based on provider."""
        if self.LLM_PROVIDER == "openai":
            return self.OPENAI_MODEL
        return self.OLLAMA_MODEL
    
    @property
    def active_embedding_model(self) -> str:
        """Get the active embedding model based on provider."""
        if self.LLM_PROVIDER == "openai":
            return self.OPENAI_EMBEDDING_MODEL
        return self.OLLAMA_EMBEDDING_MODEL
    
    @property
    def active_embedding_dimensions(self) -> int:
        """
        Return appropriate embedding dimensions based on active provider/model.
        OpenAI text-embedding-3-small: 1536
        OpenAI text-embedding-3-large: 3072
        Ollama nomic-embed-text: 768
        Ollama mxbai-embed-large: 1024
        """
        if self.LLM_PROVIDER == "ollama":
            if self.OLLAMA_EMBEDDING_MODEL == "nomic-embed-text":
                return 768
            elif self.OLLAMA_EMBEDDING_MODEL == "mxbai-embed-large":
                return 1024
        return self.EMBEDDING_DIMENSIONS
    
    @field_validator("OLLAMA_BASE_URL")
    @classmethod
    def fix_ollama_docker_url(cls, v: str) -> str:
        """
        Handle Ollama URL for Docker environments.
        When running in Docker, Ollama on host needs host.docker.internal.
        """
        is_in_docker = os.path.exists("/.dockerenv")
        if is_in_docker and "localhost" in v:
            return v.replace("localhost", "host.docker.internal")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()  # type: ignore


settings = get_settings()