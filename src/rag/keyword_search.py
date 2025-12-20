from typing import List, Dict, Any

from src.services.database.supabase import supabase


class KeywordSearch:
    """Full-text keyword search using PostgreSQL GIN index."""
    
    def __init__(self):
        self.db = supabase
    
    def search(
        self,
        query: str,
        document_ids: List[str],
        chunks_per_search: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform full-text keyword search.
        
        Args:
            query: Search query string
            document_ids: List of document IDs to search within
            chunks_per_search: Maximum number of results
            
        Returns:
            List of matching chunks with BM25-style scores
        """
        result = self.db.rpc(
            "keyword_search_document_chunks",
            {
                "query_text": query,
                "filter_document_ids": document_ids,
                "chunks_per_search": chunks_per_search
            }
        ).execute()
        
        return result.data if result.data else []


# Default instance
keyword_search = KeywordSearch()
