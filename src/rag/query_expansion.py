from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from src.schemas.chat import QueryVariations
from src.services.llm.chat import chat_service
from src.services.llm.providers.openrouter import OpenRouterProvider


def generate_query_variations(
    original_query: str,
    num_queries: int = 3
) -> List[str]:
    """
    Generate query variations using LLM for multi-query retrieval.
    
    Args:
        original_query: The original user query
        num_queries: Total number of queries to return (including original)
        
    Returns:
        List of query strings (original + variations)
        
    Example:
        >>> queries = generate_query_variations("How does photosynthesis work?", 3)
        >>> # Returns: ["How does photosynthesis work?", 
        >>> #          "What is the process of photosynthesis?",
        >>> #          "Explain plant energy conversion"]
    """
    system_prompt = f"""Generate {num_queries - 1} alternative ways to phrase this question for document search. 
Use different keywords and synonyms while maintaining the same intent. 
Return exactly {num_queries - 1} variations."""
    
    try:
        provider = OpenRouterProvider()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original query: {original_query}"}
        ]
        
        result = provider.chat_with_structured_output(
            messages=messages,
            output_schema=QueryVariations
        )
        
        # Return original query + variations
        variations = result.queries[:num_queries - 1]
        return [original_query] + variations
        
    except Exception as e:
        print(f"⚠️ Query variation generation failed: {e}")
        return [original_query]


def expand_query_with_context(
    query: str,
    chat_history: List[dict] = None
) -> str:
    """
    Expand query using chat history context.
    
    Args:
        query: Current user query
        chat_history: Previous messages in the conversation
        
    Returns:
        Expanded query string
    """
    if not chat_history:
        return query
    
    # Build context from recent messages
    recent_context = ""
    for msg in chat_history[-4:]:  # Last 4 messages
        role = msg.get("role", "user")
        content = msg.get("content", "")[:200]
        recent_context += f"{role}: {content}\n"
    
    system_prompt = """Given the conversation context, rewrite the user's query to be self-contained and clear.
Include any relevant context from the conversation that would help with document retrieval.
Return only the rewritten query, nothing else."""
    
    try:
        provider = OpenRouterProvider()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{recent_context}\n\nQuery: {query}"}
        ]
        
        expanded = provider.chat(messages)
        return expanded.strip()
        
    except Exception:
        return query
