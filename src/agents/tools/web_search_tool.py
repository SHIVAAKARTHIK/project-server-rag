"""
Web Search Tool (Tavily)

This tool allows the agent to search the internet for current information.
Used when documents don't contain the answer and query needs external data.

Setup:
    1. Get API key from https://tavily.com
    2. Add TAVILY_API_KEY to your .env file

Usage:
    from src.agents.tools.web_search_tool import web_search_tool, execute_web_search
"""

from typing import List, Dict, Any, Tuple
from langchain_core.tools import tool

from src.config import settings


# Initialize Tavily client lazily
_tavily_client = None


def _get_tavily_client():
    """Get or create Tavily client."""
    global _tavily_client
    
    if _tavily_client is None:
        try:
            from tavily import TavilyClient
            _tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        except ImportError:
            raise ImportError("Please install tavily-python: pip install tavily-python")
        except Exception as e:
            raise ValueError(f"Failed to initialize Tavily client: {e}")
    
    return _tavily_client


@tool
def web_search_tool(query: str) -> str:
    """
    Search the internet for current information.
    
    Use this tool when:
    - User asks about current events, news, or recent happenings
    - User asks about weather, stock prices, or real-time data
    - User asks about topics not found in their documents
    - User asks to compare document info with external sources
    - Query requires up-to-date information from the internet
    
    Do NOT use this tool when:
    - User is just saying hello or making small talk
    - User asks about their uploaded documents
    - Question can be answered from general knowledge
    
    Args:
        query: The search query to find information on the internet
        
    Returns:
        Relevant information from web search results
    """
    # Placeholder - actual execution happens in tool_node
    return f"Searching the web for: {query}"


def execute_web_search(
    query: str,
    max_results: int = 5
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Execute web search using Tavily.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        Tuple of (formatted_context, sources)
        - formatted_context: String with search results for LLM
        - sources: List of source dicts with url, title
    """
    print(f"\n🌐 WEB SEARCH - Executing Tavily search")
    print(f"📝 Query: {query[:100]}...")
    
    try:
        client = _get_tavily_client()
        
        # Execute search
        response = client.search(
            query=query,
            max_results=max_results,
            include_answer=True,  # Get AI-generated summary
            include_raw_content=False,
            search_depth="basic"  # "basic" or "advanced"
        )
        
        # Extract results
        results = response.get("results", [])
        answer = response.get("answer", "")
        
        print(f"✅ Found {len(results)} results")
        
        if not results:
            return "No relevant information found on the web.", []
        
        # Format context for LLM
        formatted_context = _format_web_results(results, answer)
        
        # Extract sources
        sources = [
            {
                "url": r.get("url", ""),
                "title": r.get("title", "Unknown"),
                "snippet": r.get("content", "")[:200]
            }
            for r in results
        ]
        
        return formatted_context, sources
        
    except Exception as e:
        print(f"❌ Web search error: {str(e)}")
        return f"Error searching the web: {str(e)}", []


def _format_web_results(
    results: List[Dict[str, Any]],
    answer: str = ""
) -> str:
    """
    Format web search results for the LLM.
    
    Args:
        results: List of search results from Tavily
        answer: AI-generated summary from Tavily (optional)
        
    Returns:
        Formatted string with search results
    """
    parts = []
    
    # Add Tavily's AI summary if available
    if answer:
        parts.append(f"**Summary:** {answer}")
        parts.append("")
    
    # Add individual results
    parts.append("**Sources:**")
    for i, result in enumerate(results, 1):
        title = result.get("title", "Unknown")
        url = result.get("url", "")
        content = result.get("content", "")[:500]  # Limit content length
        
        parts.append(f"\n[{i}] {title}")
        parts.append(f"URL: {url}")
        parts.append(f"Content: {content}")
        parts.append("")
    
    return "\n".join(parts)


__all__ = ["web_search_tool", "execute_web_search"]