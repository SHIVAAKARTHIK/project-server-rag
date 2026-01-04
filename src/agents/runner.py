"""
Agent Runner

This is the main entry point for running agents.
It provides a clean interface that hides the complexity of state management.

Usage:
    from src.agents.runner import run_simple_agent
    
    result = run_simple_agent(
        query="What does the doc say about AI?",
        chat_history=[...],
        document_ids=["doc-123"],
        settings={"llm_provider": "openai"}
    )
    
    print(result["response"])
    print(result["citations"])
"""

from typing import List, Dict, Any, Optional

from src.agents.state import AgentState, create_initial_state
from src.agents.graphs.simple_agent import get_simple_agent
from src.agents.graphs.agentic_agent import get_agentic_agent


class AgentResult:
    """
    Result from agent execution.
    
    Provides easy access to response and citations.
    """
    
    def __init__(self, state: Dict[str, Any]):
        self._state = state
    
    @property
    def response(self) -> str:
        """The generated response text."""
        return self._state.get("response", "")
    
    @property
    def citations(self) -> List[Dict[str, Any]]:
        """List of citations from RAG search."""
        return self._state.get("citations", [])
    
    @property
    def has_results(self) -> bool:
        """Whether RAG search found relevant results."""
        return self._state.get("has_results", False)
    
    @property
    def tool_used(self) -> bool:
        """Whether a tool was used (RAG search)."""
        return bool(self._state.get("tool_output", ""))
    
    @property
    def tool_output(self) -> str:
        """Raw output from tool execution."""
        return self._state.get("tool_output", "")
    
    @property
    def web_sources(self) -> List[Dict[str, Any]]:
        """List of web sources (for agentic agent)."""
        return self._state.get("web_sources", [])
    
    @property
    def used_web_search(self) -> bool:
        """Whether web search was used (for agentic agent)."""
        return bool(self._state.get("web_output", ""))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "response": self.response,
            "citations": self.citations,
            "has_results": self.has_results,
            "web_sources": self.web_sources,
            "used_web_search": self.used_web_search
        }
    
    def __repr__(self) -> str:
        return f"AgentResult(response='{self.response[:50]}...', citations={len(self.citations)}, has_results={self.has_results})"


def run_simple_agent(
    query: str,
    chat_history: List[Dict[str, Any]],
    document_ids: List[str],
    settings: Dict[str, Any]
) -> AgentResult:
    """
    Run the simple RAG agent.
    
    This is the main entry point for using the agent.
    It handles state creation and graph invocation.
    
    Args:
        query: User's current question/message
        chat_history: Previous messages in conversation
            Format: [{"role": "user", "content": "..."}, ...]
        document_ids: List of document IDs available for search
        settings: Project settings including:
            - llm_provider: "openai" or "ollama"
            - rag_strategy: "basic", "hybrid", etc.
            - chunks_per_search: int
            - similarity_threshold: float
            
    Returns:
        AgentResult with response and citations
        
    Example:
        result = run_simple_agent(
            query="Hi I am Karthik",
            chat_history=[],
            document_ids=["doc-123", "doc-456"],
            settings={"llm_provider": "openai", "rag_strategy": "basic"}
        )
        
        print(result.response)    # "Hi Karthik! How can I help?"
        print(result.citations)   # []
        print(result.tool_used)   # False
        
        # For document questions
        result = run_simple_agent(
            query="What does the doc say about sleep?",
            chat_history=[],
            document_ids=["doc-123"],
            settings={"llm_provider": "openai"}
        )
        
        print(result.response)    # "According to the document..."
        print(result.citations)   # [{"chunk_id": "...", "filename": "...", "page": 5}]
        print(result.tool_used)   # True
    """
    print("\n" + "="*60)
    print("🚀 SIMPLE AGENT - Starting execution")
    print("="*60)
    print(f"📝 Query: {query[:100]}...")
    print(f"📄 Documents: {len(document_ids)}")
    print(f"💬 Chat history: {len(chat_history)} messages")
    print(f"⚙️  Provider: {settings.get('llm_provider', 'openai')}")
    
    # Create initial state
    initial_state = create_initial_state(
        query=query,
        chat_history=chat_history,
        document_ids=document_ids,
        settings=settings
    )
    
    # Get the agent graph
    agent = get_simple_agent()
    
    # Run the agent
    print("\n🔄 Executing agent graph...")
    final_state = agent.invoke(initial_state)
    
    # Wrap result
    result = AgentResult(final_state)
    
    print("\n" + "="*60)
    print("✅ SIMPLE AGENT - Execution complete")
    print(f"📊 Found relevant docs: {result.has_results}")
    print(f"📚 Citations: {len(result.citations)}")
    print(f"💬 Response length: {len(result.response)} chars")
    print("="*60 + "\n")
    
    return result


async def run_simple_agent_async(
    query: str,
    chat_history: List[Dict[str, Any]],
    document_ids: List[str],
    settings: Dict[str, Any]
) -> AgentResult:
    """
    Async version of run_simple_agent.
    
    For use in async endpoints.
    
    Args:
        Same as run_simple_agent
        
    Returns:
        AgentResult with response and citations
    """
    # For now, just wrap the sync version
    # LangGraph supports async natively if needed
    return run_simple_agent(
        query=query,
        chat_history=chat_history,
        document_ids=document_ids,
        settings=settings
    )


def run_agentic_agent(
    query: str,
    chat_history: List[Dict[str, Any]],
    document_ids: List[str],
    settings: Dict[str, Any]
) -> AgentResult:
    """
    Run the agentic RAG agent with web search capability.
    
    Flow:
    1. Always search documents first (RAG)
    2. If docs have answer → respond with doc context
    3. If no docs → agent decides: web search or direct response
    
    Args:
        query: User's current question/message
        chat_history: Previous messages in conversation
        document_ids: List of document IDs available for search
        settings: Project settings including llm_provider, rag_strategy, etc.
            
    Returns:
        AgentResult with response, citations, and web_sources
        
    Example:
        result = run_agentic_agent(
            query="What's the latest news about AI?",
            chat_history=[],
            document_ids=["doc-123"],
            settings={"llm_provider": "openai"}
        )
        
        print(result.response)       # Answer from web
        print(result.citations)      # [] (no docs used)
        print(result.web_sources)    # [{url: "...", title: "..."}]
        print(result.used_web_search)  # True
    """
    print("\n" + "="*60)
    print("🚀 AGENTIC AGENT - Starting execution")
    print("="*60)
    print(f"📝 Query: {query[:100]}...")
    print(f"📄 Documents: {len(document_ids)}")
    print(f"💬 Chat history: {len(chat_history)} messages")
    print(f"⚙️  Provider: {settings.get('llm_provider', 'openai')}")
    
    # Create initial state
    initial_state = create_initial_state(
        query=query,
        chat_history=chat_history,
        document_ids=document_ids,
        settings=settings
    )
    
    # Get the agentic agent graph
    agent = get_agentic_agent()
    
    # Run the agent
    print("\n🔄 Executing agentic agent graph...")
    final_state = agent.invoke(initial_state)
    
    # Wrap result
    result = AgentResult(final_state)
    
    print("\n" + "="*60)
    print("✅ AGENTIC AGENT - Execution complete")
    print(f"📊 Found in docs: {result.has_results}")
    print(f"📚 Doc citations: {len(result.citations)}")
    print(f"🌐 Used web search: {result.used_web_search}")
    print(f"🔗 Web sources: {len(result.web_sources)}")
    print(f"💬 Response length: {len(result.response)} chars")
    print("="*60 + "\n")
    
    return result


async def run_agentic_agent_async(
    query: str,
    chat_history: List[Dict[str, Any]],
    document_ids: List[str],
    settings: Dict[str, Any]
) -> AgentResult:
    """
    Async version of run_agentic_agent.
    
    For use in async endpoints.
    """
    return run_agentic_agent(
        query=query,
        chat_history=chat_history,
        document_ids=document_ids,
        settings=settings
    )


__all__ = [
    "AgentResult",
    "run_simple_agent",
    "run_simple_agent_async",
    "run_agentic_agent",
    "run_agentic_agent_async",
]