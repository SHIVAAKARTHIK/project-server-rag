"""
RAG Search Tool

This tool allows the agent to search through uploaded documents.
It uses the existing RAGPipeline for retrieval.

Usage:
    from src.agents.tools.rag_tool import rag_search_tool, execute_rag_search
"""

from typing import List, Dict, Any, Tuple
from langchain_core.tools import tool

from src.rag.pipeline import RAGPipeline
from src.rag.context_builder import build_context


# Reuse existing pipeline instance
rag_pipeline = RAGPipeline()


@tool
def rag_search_tool(query: str) -> str:
    """
    Search through uploaded documents to find relevant information.
    
    Use this tool when:
    - User asks about content in their documents
    - User asks questions that require information from uploaded files
    - User wants to know what their documents say about a topic
    - User references "the document", "the file", "my upload", etc.
    
    Do NOT use this tool when:
    - User is just saying hello or making small talk
    - User asks general knowledge questions not related to their documents
    - User asks about current events or real-time information
    
    Args:
        query: The search query to find relevant document content
        
    Returns:
        Relevant context extracted from the user's documents
    """
    # Placeholder - actual execution happens in tool_node
    return f"Searching documents for: {query}"


def execute_rag_search(
    query: str,
    document_ids: List[str],
    settings: Dict[str, Any]
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Execute RAG search using existing RAGPipeline.
    
    This only does RETRIEVAL, not LLM generation.
    The agent will handle response generation.
    
    Args:
        query: Search query
        document_ids: List of document IDs to search
        settings: Project settings with RAG configuration
        
    Returns:
        Tuple of (formatted_context, citations)
    """
    if not document_ids:
        return "No documents available to search.", []
    
    print(f"\n🔍 RAG Tool - Executing search")
    print(f"📄 Searching {len(document_ids)} documents")
    
    # Use RAGPipeline's internal _retrieve method
    strategy = settings.get("rag_strategy", "basic")
    chunks = rag_pipeline._retrieve(query, document_ids, settings, strategy)
    
    if not chunks:
        return "No relevant information found in the documents.", []
    
    # Trim to final context size
    final_size = settings.get("final_context_size", 5)
    chunks = chunks[:final_size]
    print(f"📄 Using {len(chunks)} chunks for context")
    
    # Use existing context builder
    texts, images, tables, citations = build_context(chunks)
    
    # Format context for agent
    formatted_context = _format_context_for_agent(texts, chunks)
    
    # Convert citations to dict format
    citations_list = [c.model_dump() for c in citations]
    
    return formatted_context, citations_list


def _format_context_for_agent(
    texts: List[str],
    chunks: List[Dict[str, Any]]
) -> str:
    """
    Format retrieved context for the agent.
    
    Includes source attribution for each chunk.
    """
    if not texts:
        return "No relevant content found in documents."
    
    context_parts = []
    
    for i, (text, chunk) in enumerate(zip(texts, chunks), 1):
        filename = chunk.get("filename", "Unknown")
        page = chunk.get("page_number", 1)
        
        context_parts.append(
            f"[Source {i}: {filename}, Page {page}]\n{text}"
        )
    
    return "\n\n---\n\n".join(context_parts)


__all__ = ["rag_search_tool", "execute_rag_search"]