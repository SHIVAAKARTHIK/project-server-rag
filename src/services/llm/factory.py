from typing import Literal

from src.config import settings
from src.services.llm.providers.base import BaseLLMProvider, BaseEmbeddingProvider
from src.services.llm.providers.openai import OpenAIProvider, OpenAIEmbeddingProvider
from src.services.llm.providers.ollama import OllamaProvider, OllamaEmbeddingProvider


ProviderType = Literal["openai", "ollama"]


class LLMProviderFactory:
    """Factory for creating LLM and embedding providers based on configuration."""
    
    @staticmethod
    def get_llm_provider(
        provider: ProviderType = None,
        model: str = None,
        temperature: float = 0
    ) -> BaseLLMProvider:
        """
        Get an LLM provider instance.
        
        Args:
            provider: Provider type ("openai" or "ollama"). Defaults to settings.LLM_PROVIDER
            model: Model name. Defaults to provider's default model.
            temperature: Temperature for generation. Defaults to 0.
            
        Returns:
            BaseLLMProvider instance
        """
        provider = provider or settings.LLM_PROVIDER
        
        if provider == "openai":
            # Use OpenAI model
            model = model or settings.OPENAI_MODEL
            print(f"🔧 Creating OpenAI provider with model: {model}")
            return OpenAIProvider(model=model, temperature=temperature)
        elif provider == "ollama":
            # Use Ollama model - IMPORTANT: Don't use OpenAI model here!
            model = model or settings.OLLAMA_MODEL
            print(f"🔧 Creating Ollama provider with model: {model}")
            return OllamaProvider(model=model, temperature=temperature)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    @staticmethod
    def get_embedding_provider(
        provider: ProviderType = None,
        model: str = None,
        dimensions: int = None
    ) -> BaseEmbeddingProvider:
        """
        Get an embedding provider instance.
        
        Args:
            provider: Provider type ("openai" or "ollama"). Defaults to settings.LLM_PROVIDER
            model: Model name. Defaults to provider's default embedding model.
            dimensions: Embedding dimensions (only for OpenAI).
            
        Returns:
            BaseEmbeddingProvider instance
        """
        provider = provider or settings.LLM_PROVIDER
        
        if provider == "openai":
            model = model or settings.OPENAI_EMBEDDING_MODEL
            print(f"🔧 Creating OpenAI embedding provider with model: {model}")
            return OpenAIEmbeddingProvider(model=model, dimensions=dimensions)
        elif provider == "ollama":
            model = model or settings.OLLAMA_EMBEDDING_MODEL
            print(f"🔧 Creating Ollama embedding provider with model: {model}")
            return OllamaEmbeddingProvider(model=model)
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")


# Convenience functions for quick access
def get_llm(
    provider: ProviderType = None,
    model: str = None,
    temperature: float = 0
) -> BaseLLMProvider:
    """Shortcut to get an LLM provider."""
    return LLMProviderFactory.get_llm_provider(provider, model, temperature)


def get_embeddings(
    provider: ProviderType = None,
    model: str = None
) -> BaseEmbeddingProvider:
    """Shortcut to get an embedding provider."""
    return LLMProviderFactory.get_embedding_provider(provider, model)