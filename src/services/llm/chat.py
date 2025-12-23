from typing import List, Any, Optional
from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage,BaseMessage

from src.services.llm.providers.openrouter import OpenRouterProvider
from src.config import settings


class ChatService:
    """Service for LLM chat completions."""
    
    def __init__(self, model: str = None, temperature: float = 0):
        self.provider = OpenRouterProvider(
            model=model,
            temperature=temperature
        )
    
    def chat(
        self,
        messages: List[dict],
        temperature: float = 0,
        **kwargs
    ) -> str:
        """Generate a chat completion."""
        return self.provider.chat(messages, temperature, **kwargs)
    
    def chat_with_structured_output(
        self,
        messages: List[dict],
        output_schema: Any,
        **kwargs
    ) -> Any:
        """Generate structured output from chat."""
        return self.provider.chat_with_structured_output(
            messages,
            output_schema,
            **kwargs
        )
    
    def invoke_multimodal(
        self,
        system_prompt: str,
        user_query: str,
        images: Optional[List[str]] = None
    ) -> str:
        """
        Invoke LLM with multi-modal support (text + images).
        
        Args:
            system_prompt: System instructions
            user_query: User's question
            images: List of base64-encoded images
            
        Returns:
            LLM response content
        """
        
        messages = [SystemMessage(content=system_prompt)]
        
        if images:
            # Multi-modal message
            content_parts = [{"type": "text", "text": user_query}]
            
            for img_base64 in images:
                # Clean base64 if needed
                if img_base64.startswith("data:image"):
                    img_base64 = img_base64.split(",", 1)[1]
                
                content_parts.append({  # pyright: ignore[reportArgumentType]
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                })
            
            user_message = HumanMessage(content=content_parts)  # pyright: ignore[reportArgumentType]
        else:
            user_message = HumanMessage(content=content_parts)  # pyright: ignore[reportUnboundVariable]
        
        messages: List[BaseMessage] = [
        SystemMessage(content=system_prompt),
        user_message
    ]
        return self.provider.invoke_with_images(messages)


@lru_cache
def get_chat_service() -> ChatService:
    """Get cached chat service instance."""
    return ChatService()


# Default instance
chat_service = get_chat_service()
