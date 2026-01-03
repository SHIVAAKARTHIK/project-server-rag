"""
Agents Module

This module contains LangGraph-based agents for the RAG system.

Available Agents:
- SimpleAgent: Single agent with RAG tool (decides: direct answer or search docs)
- AgenticAgent: Agent with RAG + Web Search tools (future)

Usage:
    from src.agents import run_simple_agent
    
    result = run_simple_agent(
        query="What does the doc say?",
        chat_history=[...],
        document_ids=["doc-123"],
        settings={"llm_provider": "openai"}
    )
    
    print(result.response)
    print(result.citations)
"""

from src.agents.state import AgentState, create_initial_state
from src.agents.runner import AgentResult, run_simple_agent, run_simple_agent_async
from src.agents.graphs.simple_agent import build_simple_agent, get_simple_agent

__all__ = [
    # State
    "AgentState",
    "create_initial_state",
    
    # Runner (main entry point)
    "AgentResult",
    "run_simple_agent",
    "run_simple_agent_async",
    
    # Graph builders
    "build_simple_agent",
    "get_simple_agent",
]