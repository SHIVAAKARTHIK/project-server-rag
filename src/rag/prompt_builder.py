from typing import List, Optional

from src.services.llm.factory import get_llm
from src.rag.context_builder import format_context_for_prompt


RAG_SYSTEM_PROMPT_TEMPLATE = """You are a helpful AI assistant that answers questions based solely on the provided context.
Your task is to provide accurate, detailed answers using ONLY the information available in the context below.

IMPORTANT RULES:
- Only answer based on the provided context (texts, tables, and images)
- If the answer cannot be found in the context, respond with: 'I don't have enough information in the provided context to answer that question.'
- Do not use external knowledge or make assumptions beyond what's explicitly stated
- When referencing information, be specific and cite relevant parts of the context
- Synthesize information from texts, tables, and images to provide comprehensive answers

{context}

Based on all the context provided above (documents, tables, and images), please answer the user's question accurately and comprehensively.
"""


def build_system_prompt(
    texts: List[str],
    tables: List[str],
    images: List[str]
) -> str:
    """
    Build the complete system prompt with context.
    
    Args:
        texts: List of text chunks
        tables: List of HTML table strings
        images: List of base64 images
        
    Returns:
        Complete system prompt string
    """
    context = format_context_for_prompt(texts, tables, images)
    return RAG_SYSTEM_PROMPT_TEMPLATE.format(context=context)


def prepare_prompt_and_invoke_llm(
    user_query: str,
    texts: List[str],
    images: Optional[List[str]] = None,
    tables: Optional[List[str]] = None,
    llm_provider: str = "openai"
) -> str:
    """
    Build complete RAG prompt and invoke LLM.
    
    Handles multi-modal content (text + images) when images are present.
    
    Args:
        user_query: The user's question
        texts: List of text chunks from documents
        images: Optional list of base64-encoded images
        tables: Optional list of HTML table strings
        llm_provider: LLM provider to use ("openai" or "ollama")
        
    Returns:
        AI response string
        
    Example:
        >>> response = prepare_prompt_and_invoke_llm(
        ...     user_query="What are the key findings?",
        ...     texts=["Finding 1: ...", "Finding 2: ..."],
        ...     images=[base64_image],
        ...     tables=["<table>...</table>"],
        ...     llm_provider="openai"
        ... )
    """
    images = images or []
    tables = tables or []
    
    # Build system prompt with context
    system_prompt = build_system_prompt(texts, tables, images)
    
    # Get LLM based on provider
    llm = get_llm(provider=llm_provider)
    
    print(
        f"🤖 Invoking LLM ({llm_provider}) with {len(texts)} texts, "
        f"{len(tables)} tables, {len(images)} images..."
    )
    
    # Use multi-modal invocation if images present
    response = llm.invoke_with_images(
        messages=_build_multimodal_messages(
            system_prompt=system_prompt,
            user_query=user_query,
            images=images if images else None
        )
    )
    
    return response


def _build_multimodal_messages(
    system_prompt: str,
    user_query: str,
    images: Optional[List[str]] = None
) -> List:
    """
    Build message list for multi-modal LLM invocation.
    
    Args:
        system_prompt: System instructions with context
        user_query: User's question
        images: Optional list of base64-encoded images
        
    Returns:
        List of LangChain message objects
    """
    from langchain_core.messages import HumanMessage, SystemMessage
    
    messages = [SystemMessage(content=system_prompt)]
    
    if images:
        # Multi-modal message with images
        content_parts = [{"type": "text", "text": user_query}]
        
        for img_base64 in images:
            # Clean base64 if needed
            if img_base64.startswith("data:image"):
                img_base64 = img_base64.split(",", 1)[1]
            
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
            })
        
        messages.append(HumanMessage(content=content_parts))
    else:
        # Text-only message
        messages.append(HumanMessage(content=user_query))
    
    return messages


def prepare_simple_prompt(
    user_query: str,
    context: str,
    llm_provider: str = "openai"
) -> str:
    """
    Build a simple prompt without multi-modal support.
    
    Args:
        user_query: The user's question
        context: Pre-formatted context string
        llm_provider: LLM provider to use ("openai" or "ollama")
        
    Returns:
        AI response string
    """
    system_prompt = RAG_SYSTEM_PROMPT_TEMPLATE.format(context=context)
    
    # Get LLM based on provider
    llm = get_llm(provider=llm_provider)
    
    return llm.chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ])