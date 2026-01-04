"""
Agent Graphs Module

Contains LangGraph workflow definitions.

Graphs:
- simple_agent: Always RAG first, direct response if no results
- agentic_agent: RAG first, then web search if needed
- streaming_agent: Agentic agent with real-time streaming

Update your existing file at: src/agents/graphs/__init__.py
"""

from src.agents.graphs.simple_agent import build_simple_agent, get_simple_agent
from src.agents.graphs.agentic_agent import build_agentic_agent, get_agentic_agent
from src.agents.graphs.streaming_agent import stream_agentic_agent  # NEW

__all__ = [
    "build_simple_agent",
    "get_simple_agent",
    "build_agentic_agent",
    "get_agentic_agent",
    "stream_agentic_agent",  # NEW
]