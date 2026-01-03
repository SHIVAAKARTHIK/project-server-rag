"""
Agent Node

Simplified version that ALWAYS triggers RAG search first.
The respond_node will handle the case when no results are found.

Usage:
    from src.agents.nodes.agent_node import agent_node
"""

from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.agents.state import AgentState


# Simple prompt - we're not asking LLM to decide, just preparing context
AGENT_SYSTEM_PROMPT = """You are a helpful AI assistant. 
You will be provided with context from the user's documents to answer their question.
If no relevant context is found, you'll answer based on your general knowledge.
"""


def agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Agent node - prepares for RAG search.
    
    This simplified version always proceeds to RAG search.
    No LLM call here - just pass through to tool_node.
    
    Args:
        state: Current agent state with query, chat_history, settings
        
    Returns:
        Dict with search query for tool_node
    """
    print("\n🤖 AGENT NODE - Preparing RAG search...")
    print(f"💬 Query: {state['query'][:100]}...")
    print(f"📄 Documents available: {len(state.get('document_ids', []))}")
    
    # Always proceed to RAG search - no decision needed
    # Just pass the query forward
    return {
        "search_query": state["query"]
    }


__all__ = ["agent_node", "AGENT_SYSTEM_PROMPT"]