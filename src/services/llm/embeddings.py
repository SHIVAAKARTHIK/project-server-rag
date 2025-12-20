from typing import List
from functools import lru_cache

from src.services.llm.providers.openrouter import OpenRouterEmbeddingProvider
from src.config import settings


class EmbeddingService:
    """Service for generating embeddings."""
    
    def __init__(self, model: str = None, dimensions: int = None):
        self.provider = OpenRouterEmbeddingProvider(
            model=model,
            dimensions=dimensions
        )
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query."""
        return self.provider.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        return self.provider.embed_documents(texts)
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 10
    ) -> List[List[float]]:
        """Generate embeddings in batches."""
        return self.provider.embed_batch(texts, batch_size)


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    return EmbeddingService()


# Default instance
embedding_service = get_embedding_service()
