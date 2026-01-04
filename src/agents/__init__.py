"""
Agents Module

This module contains LangGraph-based agents for the RAG system.

Available Agents:
- SimpleAgent: Always RAG first, direct response if no results
- AgenticAgent: RAG first, then web search if needed

Usage:
    # Simple Agent (RAG only)
    from src.agents import run_simple_agent
    
    result = run_simple_agent(
        query="What does the doc say?",
        chat_history=[...],
        document_ids=["doc-123"],
        settings={"llm_provider": "openai"}
    )
    
    # Agentic Agent (RAG + Web Search)
    from src.agents import run_agentic_agent
    
    result = run_agentic_agent(
        query="What's the latest AI news?",
        chat_history=[...],
        document_ids=["doc-123"],
        settings={"llm_provider": "openai"}
    )
"""

from src.agents.state import AgentState, create_initial_state
from src.agents.runner import (
    AgentResult,
    run_simple_agent,
    run_simple_agent_async,
    run_agentic_agent,
    run_agentic_agent_async,
)
from src.agents.graphs.simple_agent import build_simple_agent, get_simple_agent
from src.agents.graphs.agentic_agent import build_agentic_agent, get_agentic_agent

__all__ = [
    # State
    "AgentState",
    "create_initial_state",
    
    # Runner (main entry points)
    "AgentResult",
    "run_simple_agent",
    "run_simple_agent_async",
    "run_agentic_agent",
    "run_agentic_agent_async",
    
    # Graph builders
    "build_simple_agent",
    "get_simple_agent",
    "build_agentic_agent",
    "get_agentic_agent",
]