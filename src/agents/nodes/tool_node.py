"""
Tool Node

Executes RAG search on every query.
Always searches documents first, respond_node handles empty results.

Usage:
    from src.agents.nodes.tool_node import tool_node
"""

from typing import Dict, Any

from src.agents.state import AgentState
from src.agents.tools.rag_tool import execute_rag_search


def tool_node(state: AgentState) -> Dict[str, Any]:
    """
    Tool execution node - ALWAYS runs RAG search.
    
    This node:
    1. Takes the user query
    2. Executes RAG search against documents
    3. Returns context and citations
    
    The respond_node will handle cases where no results are found.
    
    Args:
        state: Current agent state with query, document_ids, settings
        
    Returns:
        Dict with:
        - tool_output: Retrieved context (or empty message)
        - citations: List of citations (or empty list)
        - has_results: Boolean indicating if relevant docs found
    """
    print("\n🔧 TOOL NODE - Executing RAG search...")
    
    query = state["query"]
    document_ids = state.get("document_ids", [])
    settings = state.get("settings", {})
    
    print(f"📝 Query: {query[:100]}...")
    print(f"📄 Documents: {len(document_ids)} available")
    
    # If no documents, skip search
    if not document_ids:
        print("⚠️ No documents available, skipping search")
        return {
            "tool_output": "",
            "citations": [],
            "has_results": False
        }
    
    # Execute RAG search
    try:
        context, citations = execute_rag_search(
            query=query,
            document_ids=document_ids,
            settings=settings
        )
        
        # Check if we found relevant results
        has_results = bool(citations) and "No relevant" not in context
        
        print(f"✅ Search complete: {len(citations)} citations, has_results={has_results}")
        
        return {
            "tool_output": context,
            "citations": citations,
            "has_results": has_results
        }
        
    except Exception as e:
        print(f"❌ RAG search error: {str(e)}")
        return {
            "tool_output": "",
            "citations": [],
            "has_results": False
        }


__all__ = ["tool_node"]