from typing import List, Dict, Any

from src.services.database.supabase import supabase
from src.services.llm.embeddings import embedding_service


class VectorSearch:
    """Vector similarity search using pgvector."""
    
    def __init__(self):
        self.db = supabase
        self.embeddings = embedding_service
    
    def search(
        self,
        query: str,
        document_ids: List[str],
        match_threshold: float = 0.3,
        chunks_per_search: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.
        
        Args:
            query: Search query string
            document_ids: List of document IDs to search within
            match_threshold: Minimum similarity threshold
            chunks_per_search: Maximum number of results
            
        Returns:
            List of matching chunks with scores
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Call Supabase RPC function
        result = self.db.rpc(
            "vector_search_document_chunks",
            {
                "query_embedding": query_embedding,
                "filter_document_ids": document_ids,
                "match_threshold": match_threshold,
                "chunks_per_search": chunks_per_search
            }
        ).execute()
        
        return result.data if result.data else []
    
    def search_with_embedding(
        self,
        query_embedding: List[float],
        document_ids: List[str],
        match_threshold: float = 0.3,
        chunks_per_search: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform vector search with pre-computed embedding.
        
        Args:
            query_embedding: Pre-computed embedding vector
            document_ids: List of document IDs to search within
            match_threshold: Minimum similarity threshold
            chunks_per_search: Maximum number of results
            
        Returns:
            List of matching chunks with scores
        """
        result = self.db.rpc(
            "vector_search_document_chunks",
            {
                "query_embedding": query_embedding,
                "filter_document_ids": document_ids,
                "match_threshold": match_threshold,
                "chunks_per_search": chunks_per_search
            }
        ).execute()
        
        return result.data if result.data else []


# Default instance
vector_search = VectorSearch()
