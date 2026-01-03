"""
Respond Node

Generates the final response based on RAG results.

Two scenarios:
1. RAG found relevant results → Answer using document context
2. No relevant results → Answer directly (general knowledge + conversation)

Usage:
    from src.agents.nodes.respond_node import respond_node
"""

from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.agents.state import AgentState
from src.services.llm.factory import get_llm


# System prompt for generating response WITH context
RESPONSE_WITH_CONTEXT_PROMPT = """You are a helpful AI assistant answering questions based on document content.

You have been provided with relevant context from the user's documents. Use this context to answer their question.

## Guidelines:
- Answer based on the provided context
- Be accurate and helpful
- If the context partially answers the question, provide what you can and note any gaps
- Be conversational and friendly

## Context from documents:
{context}

Based on the above context, please answer the user's question.
"""

# System prompt for direct response (no relevant docs found)
DIRECT_RESPONSE_PROMPT = """You are a helpful AI assistant.

The user's documents were searched but no relevant information was found for this query.
Please provide a helpful response based on:
1. Your general knowledge
2. The conversation history
3. Being honest that the documents don't contain this specific information

## Guidelines:
- Be friendly and helpful
- Answer the question if you can from general knowledge
- Briefly mention that the documents don't contain specific info on this topic
- If it's a greeting or simple question, just respond naturally
"""


def respond_node(state: AgentState) -> Dict[str, Any]:
    """
    Response generation node.
    
    Checks if RAG found results and responds accordingly:
    - has_results=True → Generate answer with document context
    - has_results=False → Generate direct response
    
    Args:
        state: Current agent state with tool_output, has_results, etc.
        
    Returns:
        Dict with "response" key containing final answer
    """
    print("\n💬 RESPOND NODE - Generating response...")
    
    has_results = state.get("has_results", False)
    tool_output = state.get("tool_output", "")
    
    if has_results and tool_output:
        print("📄 Mode: Answer WITH document context")
        response = _generate_response_with_context(state)
    else:
        print("💭 Mode: Direct response (no relevant docs)")
        response = _generate_direct_response(state)
    
    print(f"✅ Response generated ({len(response)} chars)")
    
    return {"response": response}


def _generate_response_with_context(state: AgentState) -> str:
    """
    Generate response using retrieved context from RAG.
    
    Called when RAG found relevant documents.
    
    Args:
        state: Agent state with tool_output containing context
        
    Returns:
        Generated response string
    """
    # Get LLM - access internal LangChain LLM
    llm_provider = state["settings"].get("llm_provider", "openai")
    provider = get_llm(provider=llm_provider)
    llm = provider.llm  # Access raw ChatOpenAI/ChatOllama
    
    # Build system prompt with context
    context = state["tool_output"]
    system_prompt = RESPONSE_WITH_CONTEXT_PROMPT.format(context=context)
    
    # Build messages
    messages = [
        SystemMessage(content=system_prompt),
    ]
    
    # Add recent chat history for conversational context
    chat_history = state.get("chat_history", [])
    recent_history = chat_history[-4:] if len(chat_history) > 4 else chat_history
    
    for msg in recent_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    
    # Add current query
    messages.append(HumanMessage(content=state["query"]))
    
    # Generate response
    response = llm.invoke(messages)
    
    return response.content


def _generate_direct_response(state: AgentState) -> str:
    """
    Generate direct response when no relevant docs found.
    
    Uses general knowledge + conversation context.
    
    Args:
        state: Agent state with query and chat_history
        
    Returns:
        Response string
    """
    # Get LLM - access internal LangChain LLM
    llm_provider = state["settings"].get("llm_provider", "openai")
    provider = get_llm(provider=llm_provider)
    llm = provider.llm  # Access raw ChatOpenAI/ChatOllama
    
    # Build messages
    messages = [
        SystemMessage(content=DIRECT_RESPONSE_PROMPT),
    ]
    
    # Add recent chat history
    chat_history = state.get("chat_history", [])
    recent_history = chat_history[-4:] if len(chat_history) > 4 else chat_history
    
    for msg in recent_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    
    # Add current query
    messages.append(HumanMessage(content=state["query"]))
    
    # Generate response
    response = llm.invoke(messages)
    
    return response.content


__all__ = ["respond_node"]