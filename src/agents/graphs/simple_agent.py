"""
Simple Agent Graph

Simplified flow that ALWAYS searches documents first:

    ┌─────────────┐
    │   START     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   AGENT     │ ← Prepare for search
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   TOOLS     │ ← Always run RAG search
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   RESPOND   │ ← Generate answer (with or without context)
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │    END      │
    └─────────────┘

Usage:
    from src.agents.graphs.simple_agent import build_simple_agent
    
    agent = build_simple_agent()
    result = agent.invoke(initial_state)
"""

from langgraph.graph import StateGraph, END

from src.agents.state import AgentState
from src.agents.nodes.agent_node import agent_node
from src.agents.nodes.tool_node import tool_node
from src.agents.nodes.respond_node import respond_node


def build_simple_agent() -> StateGraph:
    """
    Build the Simple RAG Agent graph.
    
    Simplified flow:
    1. Agent node: Prepares query
    2. Tool node: ALWAYS runs RAG search
    3. Respond node: Generates answer based on results
    
    Returns:
        Compiled StateGraph ready for invocation
        
    Example:
        agent = build_simple_agent()
        
        result = agent.invoke({
            "query": "What is neurology?",
            "chat_history": [],
            "document_ids": ["doc-123"],
            "settings": {"llm_provider": "openai"},
            "messages": [],
            "tool_output": "",
            "has_results": False,
            "response": "",
            "citations": []
        })
        
        print(result["response"])
        print(result["citations"])
    """
    print("\n🔨 Building Simple Agent Graph...")
    
    # Create the graph with our state schema
    workflow = StateGraph(AgentState)
    
    # ============== ADD NODES ==============
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("respond", respond_node)
    
    print("✅ Added nodes: agent, tools, respond")
    
    # ============== SET ENTRY POINT ==============
    workflow.set_entry_point("agent")
    
    print("✅ Entry point: agent")
    
    # ============== ADD EDGES ==============
    # Simple linear flow: agent → tools → respond → END
    
    workflow.add_edge("agent", "tools")      # Always search docs
    workflow.add_edge("tools", "respond")    # Then respond
    workflow.add_edge("respond", END)        # Done
    
    print("✅ Added edges: agent→tools→respond→END")
    
    # ============== COMPILE ==============
    compiled = workflow.compile()
    
    print("✅ Graph compiled successfully!")
    
    return compiled


# Pre-built agent instance for convenience
simple_agent = None


def get_simple_agent() -> StateGraph:
    """
    Get or create the simple agent instance.
    
    Uses lazy initialization to avoid building graph at import time.
    
    Returns:
        Compiled SimpleAgent graph
    """
    global simple_agent
    
    if simple_agent is None:
        simple_agent = build_simple_agent()
    
    return simple_agent


__all__ = ["build_simple_agent", "get_simple_agent"]