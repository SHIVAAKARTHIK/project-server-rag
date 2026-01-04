"""
Agentic Agent Graph

RAG-first agent that uses web search when documents don't have the answer.

Flow:
    ┌─────────────┐
    │   START     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  RAG TOOL   │  Always search docs first
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ has_results?│
    └──────┬──────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
   [YES]       [NO]
     │           │
     │           ▼
     │    ┌─────────────┐
     │    │   AGENT     │  LLM decides: web or direct
     │    └──────┬──────┘
     │           │
     │     ┌─────┴─────┐
     │     │           │
     │     ▼           ▼
     │  [WEB]      [DIRECT]
     │     │           │
     │     ▼           │
     │ ┌────────┐      │
     │ │WEB TOOL│      │
     │ └───┬────┘      │
     │     │           │
     └─────┴───────────┘
           │
           ▼
    ┌─────────────┐
    │   RESPOND   │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │    END      │
    └─────────────┘

Usage:
    from src.agents.graphs.agentic_agent import build_agentic_agent
    
    agent = build_agentic_agent()
    result = agent.invoke(initial_state)
"""

from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage

from langgraph.graph import StateGraph, END

from src.agents.state import AgentState
from src.agents.tools.rag_tool import execute_rag_search
from src.agents.tools.web_search_tool import web_search_tool, execute_web_search
from src.services.llm.factory import get_llm


# System prompt for agent decision (when RAG found nothing)
AGENT_DECISION_PROMPT = """You are a helpful AI assistant deciding how to answer a question.

The user's documents have been searched but NO relevant information was found.

Now decide:
1. Use web_search_tool - if the query needs current/external information:
   - Current events, news, recent happenings
   - Weather, stock prices, real-time data
   - Information that changes frequently
   - Topics requiring internet research

2. Respond directly (don't use any tool) - if:
   - It's a greeting: "Hi", "Hello", "How are you?"
   - It's chitchat: "Tell me a joke", "What can you do?"
   - It's general knowledge you can answer without searching
   - User is asking about yourself

IMPORTANT: Only use web_search_tool if the query truly needs current/external information.
For general knowledge questions, respond directly without tools.
"""


def rag_node(state: AgentState) -> dict:
    """
    RAG search node - ALWAYS runs first.
    
    Searches documents and sets has_results flag.
    """
    print("\n🔧 RAG NODE - Searching documents first...")
    
    query = state["query"]
    document_ids = state.get("document_ids", [])
    settings = state.get("settings", {})
    
    print(f"📝 Query: {query[:100]}...")
    print(f"📄 Documents: {len(document_ids)} available")
    
    if not document_ids:
        print("⚠️ No documents available")
        return {
            "tool_output": "",
            "citations": [],
            "has_results": False
        }
    
    try:
        context, citations = execute_rag_search(
            query=query,
            document_ids=document_ids,
            settings=settings
        )
        
        has_results = bool(citations) and "No relevant" not in context
        
        print(f"✅ RAG complete: {len(citations)} citations, has_results={has_results}")
        
        return {
            "tool_output": context,
            "citations": citations,
            "has_results": has_results
        }
        
    except Exception as e:
        print(f"❌ RAG error: {str(e)}")
        return {
            "tool_output": "",
            "citations": [],
            "has_results": False
        }


def agent_decision_node(state: AgentState) -> dict:
    """
    Agent decision node - only called when RAG found nothing.
    
    LLM decides: use web search or respond directly.
    """
    print("\n🤖 AGENT DECISION NODE - RAG found nothing, deciding next step...")
    
    # Get LLM
    llm_provider = state["settings"].get("llm_provider", "openai")
    provider = get_llm(provider=llm_provider)
    llm = provider.llm
    
    print(f"📍 Using LLM provider: {llm_provider}")
    
    # Bind web search tool
    tools = [web_search_tool]
    llm_with_tools = llm.bind_tools(tools)
    
    # Build messages
    messages = [
        SystemMessage(content=AGENT_DECISION_PROMPT),
        HumanMessage(content=state["query"])
    ]
    
    # LLM decides
    response = llm_with_tools.invoke(messages)
    
    # Check decision
    if response.tool_calls:
        print(f"✅ Decision: USE WEB SEARCH")
        return {
            "messages": [response],
            "use_web_search": True
        }
    else:
        print(f"✅ Decision: DIRECT RESPONSE")
        return {
            "messages": [response],
            "use_web_search": False,
            "direct_response": response.content
        }


def web_search_node(state: AgentState) -> dict:
    """
    Web search node - called when agent decides to search web.
    """
    print("\n🌐 WEB SEARCH NODE - Searching the internet...")
    
    # Get search query from tool call
    last_message = state["messages"][-1]
    
    if last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        search_query = tool_call["args"].get("query", state["query"])
    else:
        search_query = state["query"]
    
    print(f"📝 Search query: {search_query[:100]}...")
    
    # Execute web search
    context, sources = execute_web_search(search_query)
    
    print(f"✅ Web search complete: {len(sources)} sources")
    
    return {
        "web_output": context,
        "web_sources": sources
    }


def respond_node(state: AgentState) -> dict:
    """
    Response generation node.
    
    Generates response based on available context:
    1. RAG results (has_results=True)
    2. Web search results (web_output exists)
    3. Direct response (neither)
    """
    print("\n💬 RESPOND NODE - Generating response...")
    
    has_results = state.get("has_results", False)
    web_output = state.get("web_output", "")
    direct_response = state.get("direct_response", "")
    
    # Get LLM
    llm_provider = state["settings"].get("llm_provider", "openai")
    provider = get_llm(provider=llm_provider)
    llm = provider.llm
    
    if has_results:
        # Answer from documents
        print("📄 Mode: Answer from DOCUMENTS")
        response = _generate_doc_response(state, llm)
        
    elif web_output:
        # Answer from web search
        print("🌐 Mode: Answer from WEB SEARCH")
        response = _generate_web_response(state, llm)
        
    elif direct_response:
        # Use agent's direct response
        print("💭 Mode: DIRECT response from agent")
        response = direct_response
        
    else:
        # Fallback direct response
        print("💭 Mode: FALLBACK direct response")
        response = _generate_fallback_response(state, llm)
    
    print(f"✅ Response generated ({len(response)} chars)")
    
    return {"response": response}


def _generate_doc_response(state: AgentState, llm) -> str:
    """Generate response from document context."""
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    
    prompt = f"""You are a helpful AI assistant answering questions based on document content.

## Context from documents:
{state['tool_output']}

Based on the above context, please answer the user's question.
Be accurate and helpful.
"""
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state["query"])
    ]
    
    response = llm.invoke(messages)
    return response.content


def _generate_web_response(state: AgentState, llm) -> str:
    """Generate response from web search results."""
    from langchain_core.messages import SystemMessage, HumanMessage
    
    prompt = f"""You are a helpful AI assistant answering questions based on web search results.

## Web Search Results:
{state['web_output']}

Based on the above information from the web, please answer the user's question.
Be accurate, cite sources when relevant, and mention if information might be outdated.
"""
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state["query"])
    ]
    
    response = llm.invoke(messages)
    return response.content


def _generate_fallback_response(state: AgentState, llm) -> str:
    """Generate fallback direct response."""
    from langchain_core.messages import SystemMessage, HumanMessage
    
    prompt = """You are a helpful AI assistant. 
Answer the user's question based on your general knowledge.
Be friendly and conversational.
"""
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state["query"])
    ]
    
    response = llm.invoke(messages)
    return response.content


# ============== ROUTING FUNCTIONS ==============

def route_after_rag(state: AgentState) -> Literal["respond", "agent_decision"]:
    """Route based on RAG results."""
    if state.get("has_results", False):
        print("🔀 Routing → RESPOND (has RAG results)")
        return "respond"
    else:
        print("🔀 Routing → AGENT DECISION (no RAG results)")
        return "agent_decision"


def route_after_agent(state: AgentState) -> Literal["web_search", "respond"]:
    """Route based on agent's decision."""
    if state.get("use_web_search", False):
        print("🔀 Routing → WEB SEARCH")
        return "web_search"
    else:
        print("🔀 Routing → RESPOND (direct)")
        return "respond"


# ============== BUILD GRAPH ==============

def build_agentic_agent() -> StateGraph:
    """
    Build the Agentic RAG Agent graph.
    
    Flow:
    1. RAG node: Always search docs first
    2. If has_results → respond
    3. If no results → agent decides: web search or direct
    4. Respond based on available context
    
    Returns:
        Compiled StateGraph ready for invocation
    """
    print("\n🔨 Building Agentic Agent Graph...")
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("rag", rag_node)
    workflow.add_node("agent_decision", agent_decision_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("respond", respond_node)
    
    print("✅ Added nodes: rag, agent_decision, web_search, respond")
    
    # Set entry point
    workflow.set_entry_point("rag")
    
    print("✅ Entry point: rag")
    
    # Add edges
    # After RAG: check if has results
    workflow.add_conditional_edges(
        "rag",
        route_after_rag,
        {
            "respond": "respond",
            "agent_decision": "agent_decision"
        }
    )
    
    # After agent decision: web search or respond
    workflow.add_conditional_edges(
        "agent_decision",
        route_after_agent,
        {
            "web_search": "web_search",
            "respond": "respond"
        }
    )
    
    # After web search: always respond
    workflow.add_edge("web_search", "respond")
    
    # After respond: end
    workflow.add_edge("respond", END)
    
    print("✅ Added edges: rag→(respond|agent), agent→(web|respond), web→respond, respond→END")
    
    # Compile
    compiled = workflow.compile()
    
    print("✅ Agentic Agent graph compiled successfully!")
    
    return compiled


# Pre-built instance
_agentic_agent = None


def get_agentic_agent() -> StateGraph:
    """Get or create the agentic agent instance."""
    global _agentic_agent
    
    if _agentic_agent is None:
        _agentic_agent = build_agentic_agent()
    
    return _agentic_agent


__all__ = ["build_agentic_agent", "get_agentic_agent"]