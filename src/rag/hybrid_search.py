from typing import List, Dict, Any

from src.rag.vector_search import VectorSearch
from src.rag.keyword_search import KeywordSearch
from src.rag.rrf import fuse_two_lists


class HybridSearch:
    """Hybrid search combining vector and keyword search with RRF fusion."""
    
    def __init__(self):
        self.vector_search = VectorSearch()
        self.keyword_search = KeywordSearch()
    
    def search(
        self,
        query: str,
        document_ids: List[str],
        match_threshold: float = 0.3,
        chunks_per_search: int = 10,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search with RRF fusion.
        
        Args:
            query: Search query string
            document_ids: List of document IDs to search within
            match_threshold: Similarity threshold for vector search
            chunks_per_search: Max results per search method
            vector_weight: Weight for vector search in RRF
            keyword_weight: Weight for keyword search in RRF
            
        Returns:
            Fused results sorted by RRF score
        """
        # Perform both searches
        vector_results = self.vector_search.search(
            query=query,
            document_ids=document_ids,
            match_threshold=match_threshold,
            chunks_per_search=chunks_per_search
        )
        print(f"📊 Vector Search: {len(vector_results)} chunks")
        
        keyword_results = self.keyword_search.search(
            query=query,
            document_ids=document_ids,
            chunks_per_search=chunks_per_search
        )
        print(f"📊 Keyword Search: {len(keyword_results)} chunks")
        
        # Fuse with RRF
        fused_results = fuse_two_lists(
            vector_results=vector_results,
            keyword_results=keyword_results,
            vector_weight=vector_weight,
            keyword_weight=keyword_weight
        )
        print(f"🔗 RRF Fusion: {len(fused_results)} unique chunks")
        
        return fused_results


# Default instance
hybrid_search = HybridSearch()
