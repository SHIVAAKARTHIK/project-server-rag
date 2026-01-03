"""
Agent State Definition

This module defines the state that flows through the LangGraph agent.
The state carries all necessary information between nodes:
- Input: query, chat history, document IDs, settings
- Processing: messages for LLM
- Output: response, citations

Usage:
    from src.agents.state import AgentState
"""

from typing import TypedDict, List, Dict, Any, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class Citation(TypedDict):
    """Citation structure from RAG search."""
    chunk_id: str
    document_id: str
    filename: str
    page: int


class AgentState(TypedDict):
    """
    State that flows through the agent graph.
    
    This state is passed to every node and can be read/modified.
    LangGraph automatically manages state updates between nodes.
    
    Attributes:
        query: The user's current question/message
        chat_history: Previous messages in this conversation (for context)
        document_ids: List of document IDs available for RAG search
        settings: Project settings (rag_strategy, llm_provider, etc.)
        messages: LLM message history (managed by LangGraph's add_messages)
        response: Final generated response text
        citations: List of citations from RAG search
        tool_output: Raw output from tool execution (if any)
    """
    
    # ============== INPUT ==============
    # These are provided when invoking the agent
    
    query: str
    """The user's current question or message."""
    
    chat_history: List[Dict[str, Any]]
    """
    Previous messages in this conversation.
    Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    
    document_ids: List[str]
    """List of document IDs available for RAG search in this project."""
    
    settings: Dict[str, Any]
    """
    Project settings including:
    - rag_strategy: "basic", "hybrid", etc.
    - llm_provider: "openai" or "ollama"
    - chunks_per_search: int
    - similarity_threshold: float
    - etc.
    """
    
    # ============== PROCESSING ==============
    # These are used during agent execution
    
    messages: Annotated[Sequence[BaseMessage], add_messages]
    """
    LLM message history managed by LangGraph.
    
    The `add_messages` annotation tells LangGraph to:
    - Append new messages (not replace)
    - Handle message deduplication by ID
    - Maintain proper conversation flow
    """
    
    tool_output: str
    """
    Raw output from tool execution.
    Contains retrieved context from RAG search.
    """
    
    has_results: bool
    """
    Whether RAG search found relevant results.
    Used by respond_node to decide response mode.
    """
    
    # ============== OUTPUT ==============
    # These are the final results
    
    response: str
    """The final generated response to return to the user."""
    
    citations: List[Citation]
    """
    List of citations from RAG search.
    Empty list if no documents were searched.
    """


def create_initial_state(
    query: str,
    chat_history: List[Dict[str, Any]],
    document_ids: List[str],
    settings: Dict[str, Any]
) -> AgentState:
    """
    Create initial state for agent invocation.
    
    Helper function to create a properly initialized state
    with all required fields.
    
    Args:
        query: User's question
        chat_history: Previous conversation messages
        document_ids: Available document IDs for search
        settings: Project settings
        
    Returns:
        Initialized AgentState ready for graph execution
        
    Example:
        state = create_initial_state(
            query="What does the document say about AI?",
            chat_history=[
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello! How can I help?"}
            ],
            document_ids=["doc-123", "doc-456"],
            settings={"rag_strategy": "basic", "llm_provider": "openai"}
        )
        result = agent.invoke(state)
    """
    return AgentState(
        query=query,
        chat_history=chat_history,
        document_ids=document_ids,
        settings=settings,
        messages=[],
        tool_output="",
        has_results=False,
        response="",
        citations=[]
    )