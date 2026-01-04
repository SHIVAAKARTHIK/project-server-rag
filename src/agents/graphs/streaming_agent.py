"""
Streaming Agentic Agent with Guardrails

Place this file at: src/agents/graphs/streaming_agent.py
"""

from typing import List, Dict, Any, AsyncGenerator
from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.tools.rag_tool import execute_rag_search
from src.agents.tools.web_search_tool import web_search_tool, execute_web_search
from src.agents.guardrails import (
    check_input_guardrails,
    check_output_guardrails,
    sanitize_input,
    mask_pii,
    GuardrailStatus
)
from src.services.llm.factory import get_llm


# Prompts
AGENT_DECISION_PROMPT = """You are deciding how to answer a question.
The user's documents were searched but NO relevant information was found.

Decide:
1. Use web_search_tool - for current events, news, weather, real-time data
2. Respond directly (no tool) - for greetings, chitchat, general knowledge

Only use web_search_tool if the query truly needs current/external information.
"""

DOC_RESPONSE_PROMPT = """Answer based on these document excerpts:

{context}

Be accurate and helpful. Answer the user's question.
"""

WEB_RESPONSE_PROMPT = """Answer based on these web search results:

{context}

Be accurate and cite sources when relevant.
"""

DIRECT_RESPONSE_PROMPT = """You are a helpful AI assistant. 
Answer based on your general knowledge. Be friendly and conversational.
"""


async def stream_agentic_agent(
    query: str,
    chat_history: List[Dict[str, Any]],
    document_ids: List[str],
    settings: Dict[str, Any]
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream agentic agent with guardrails.
    
    Yields:
        {"type": "status", "content": "..."}
        {"type": "token", "content": "..."}
        {"type": "citations", "content": [...]}
        {"type": "guardrail_blocked", "content": "...", "category": "..."}
        {"type": "done"}
    """
    print("\n" + "="*60)
    print("🚀 STREAMING AGENT - Starting")
    print(f"📝 Query: {mask_pii(query[:100])}...")
    print("="*60)
    
    # ==================== GUARDRAILS: INPUT CHECK ====================
    yield {"type": "status", "content": "🛡️ Checking message safety..."}
    
    # Sanitize input
    query = sanitize_input(query)
    
    # Run input guardrails
    input_result = check_input_guardrails(query)
    
    if input_result.status == GuardrailStatus.BLOCK:
        print(f"🚫 INPUT BLOCKED: {input_result.category}")
        print(f"🚫 Message: {input_result.message}")
        
        # Yield the block message - THIS IS WHAT THE USER WILL SEE
        yield {
            "type": "guardrail_blocked",
            "content": input_result.message,
            "category": input_result.category
        }
        yield {"type": "done"}
        return  # Stop processing
    
    # Log warnings but continue
    if input_result.status == GuardrailStatus.WARN:
        print(f"⚠️ Input warning: {input_result.category}")
    
    # ==================== GET LLM ====================
    llm_provider = settings.get("llm_provider", "openai")
    provider = get_llm(provider=llm_provider)
    llm = provider.llm
    
    citations = []
    
    # ==================== STEP 1: RAG SEARCH ====================
    yield {"type": "status", "content": "🔍 Searching your documents..."}
    
    has_results = False
    doc_context = ""
    
    if document_ids:
        try:
            doc_context, citations = execute_rag_search(
                query=query,
                document_ids=document_ids,
                settings=settings
            )
            has_results = bool(citations) and "No relevant" not in doc_context
            print(f"📄 RAG: {len(citations)} citations, has_results={has_results}")
        except Exception as e:
            print(f"❌ RAG error: {e}")
    
    # ==================== STEP 2: GENERATE RESPONSE ====================
    full_response = ""
    
    if has_results:
        yield {"type": "status", "content": "✅ Found in documents! Generating answer..."}
        yield {"type": "citations", "content": citations}
        
        async for token in _stream_llm_response(llm, query, doc_context, "documents"):
            full_response += token
            yield {"type": "token", "content": token}
    
    else:
        yield {"type": "status", "content": "🤔 Not found in documents. Checking if web search needed..."}
        
        use_web = await _should_use_web_search(llm, query)
        
        if use_web:
            yield {"type": "status", "content": "🌐 Searching the web..."}
            
            try:
                web_context, web_sources = execute_web_search(query)
                print(f"🌐 Web: {len(web_sources)} sources")
            except Exception as e:
                print(f"❌ Web error: {e}")
                web_context = ""
                web_sources = []
            
            if web_sources:
                yield {"type": "web_sources", "content": web_sources}
                yield {"type": "status", "content": "📝 Generating answer from web..."}
                
                async for token in _stream_llm_response(llm, query, web_context, "web"):
                    full_response += token
                    yield {"type": "token", "content": token}
            else:
                yield {"type": "status", "content": "📝 Generating response..."}
                async for token in _stream_llm_response(llm, query, "", "direct"):
                    full_response += token
                    yield {"type": "token", "content": token}
        else:
            yield {"type": "status", "content": "📝 Generating response..."}
            async for token in _stream_llm_response(llm, query, "", "direct"):
                full_response += token
                yield {"type": "token", "content": token}
    
    # ==================== GUARDRAILS: OUTPUT CHECK ====================
    output_result = check_output_guardrails(full_response, query)
    if output_result.status == GuardrailStatus.BLOCK:
        print(f"🚫 Output blocked: {output_result.category}")
    
    yield {"type": "done"}
    print("✅ Streaming complete\n")


async def _should_use_web_search(llm, query: str) -> bool:
    """Ask LLM if web search is needed."""
    tools = [web_search_tool]
    llm_with_tools = llm.bind_tools(tools)
    
    messages = [
        SystemMessage(content=AGENT_DECISION_PROMPT),
        HumanMessage(content=query)
    ]
    
    response = llm_with_tools.invoke(messages)
    
    if response.tool_calls:
        print("🤖 Decision: WEB SEARCH")
        return True
    
    print("🤖 Decision: DIRECT")
    return False


async def _stream_llm_response(llm, query: str, context: str, mode: str) -> AsyncGenerator[str, None]:
    """Stream LLM response token by token."""
    
    if mode == "documents":
        system_prompt = DOC_RESPONSE_PROMPT.format(context=context)
    elif mode == "web":
        system_prompt = WEB_RESPONSE_PROMPT.format(context=context)
    else:
        system_prompt = DIRECT_RESPONSE_PROMPT
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    
    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content


__all__ = ["stream_agentic_agent"]