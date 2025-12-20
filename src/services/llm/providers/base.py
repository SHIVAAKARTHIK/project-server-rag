from abc import ABC, abstractmethod
from typing import List, Optional, Any


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def chat(
        self,
        messages: List[dict],
        temperature: float = 0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a chat completion."""
        pass
    
    @abstractmethod
    def chat_with_structured_output(
        self,
        messages: List[dict],
        output_schema: Any,
        temperature: float = 0,
        **kwargs
    ) -> Any:
        """Generate a chat completion with structured output."""
        pass


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query."""
        pass
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        pass
