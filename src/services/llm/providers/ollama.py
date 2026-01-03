from typing import List, Optional, Any

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import settings
from src.services.llm.providers.base import BaseLLMProvider, BaseEmbeddingProvider


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider for local inference using LangChain."""
    
    def __init__(
        self,
        model: str = None,
        temperature: float = 0
    ):
        self.model = model or settings.OLLAMA_MODEL  # e.g., "qwen2.5:7b"
        self.base_url = settings.OLLAMA_BASE_URL  # e.g., "http://localhost:11434"
        
        self.llm = ChatOllama(
            model=self.model,
            temperature=temperature,
            base_url=self.base_url
        )
    
    def chat(
        self,
        messages: List[dict],
        temperature: float = 0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a chat completion."""
        langchain_messages = self._convert_messages(messages)
        
        # Ollama uses num_predict for max tokens
        invoke_kwargs = {}
        if max_tokens:
            invoke_kwargs["num_predict"] = max_tokens
            
        response = self.llm.invoke(langchain_messages, **invoke_kwargs)
        return response.content
    
    def chat_with_structured_output(
        self,
        messages: List[dict],
        output_schema: Any,
        temperature: float = 0,
        **kwargs
    ) -> Any:
        """
        Generate a chat completion with structured output.
        
        Note: Ollama's structured output support varies by model.
        Qwen2.5 and newer models support it well.
        Consider using instructor library as fallback for reliability.
        """
        langchain_messages = self._convert_messages(messages)
        structured_llm = self.llm.with_structured_output(output_schema)
        return structured_llm.invoke(langchain_messages)
    
    def invoke_with_images(
        self,
        messages: List[Any]
    ) -> str:
        """
        Invoke LLM with multi-modal messages (text + images).
        
        Note: Requires a vision-capable model like llava or bakllava.
        Qwen2.5 base models don't support vision - use qwen2-vl instead.
        """
        response = self.llm.invoke(messages)
        return response.content
    
    def _convert_messages(self, messages: List[dict]) -> List:
        """Convert dict messages to LangChain message objects."""
        langchain_messages = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))
        
        return langchain_messages


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    """Ollama embedding provider for local embeddings using LangChain."""
    
    def __init__(
        self,
        model: str = None
    ):
        # Good local embedding models: nomic-embed-text, mxbai-embed-large
        self.model = model or settings.OLLAMA_EMBEDDING_MODEL  # e.g., "nomic-embed-text"
        self.base_url = settings.OLLAMA_BASE_URL
        
        self.embeddings = OllamaEmbeddings(
            model=self.model,
            base_url=self.base_url
        )
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query."""
        return self.embeddings.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        return self.embeddings.embed_documents(texts)
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 10  # Smaller batches for local inference
    ) -> List[List[float]]:
        """Generate embeddings in batches."""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embed_documents(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings