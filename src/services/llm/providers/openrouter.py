from typing import List, Optional, Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import settings
from src.services.llm.providers.base import BaseLLMProvider, BaseEmbeddingProvider


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter LLM provider using LangChain."""
    
    def __init__(
        self,
        model: str = None,
        temperature: float = 0
    ):
        self.model = model or settings.DEFAULT_LLM_MODEL
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=temperature,
            openai_api_base=settings.OPENROUTER_BASE_URL,
            openai_api_key=settings.OPENROUTER_API_KEY
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
        response = self.llm.invoke(langchain_messages)
        return response.content
    
    def chat_with_structured_output(
        self,
        messages: List[dict],
        output_schema: Any,
        temperature: float = 0,
        **kwargs
    ) -> Any:
        """Generate a chat completion with structured output."""
        langchain_messages = self._convert_messages(messages)
        structured_llm = self.llm.with_structured_output(output_schema)
        return structured_llm.invoke(langchain_messages)
    
    def invoke_with_images(
        self,
        messages: List[Any]
    ) -> str:
        """Invoke LLM with multi-modal messages (text + images)."""
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


class OpenRouterEmbeddingProvider(BaseEmbeddingProvider):
    """OpenRouter embedding provider using LangChain."""
    
    def __init__(
        self,
        model: str = None,
        dimensions: int = None
    ):
        self.model = model or settings.DEFAULT_EMBEDDING_MODEL
        self.dimensions = dimensions or settings.EMBEDDING_DIMENSIONS
        
        self.embeddings = OpenAIEmbeddings(
            model=self.model,
            dimensions=self.dimensions,
            openai_api_base=settings.OPENROUTER_BASE_URL,
            openai_api_key=settings.OPENROUTER_API_KEY
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
        batch_size: int = 10
    ) -> List[List[float]]:
        """Generate embeddings in batches to avoid API limits."""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embed_documents(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
