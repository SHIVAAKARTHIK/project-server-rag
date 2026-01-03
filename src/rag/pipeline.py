from typing import List, Dict, Any, Optional

from src.models.enums import RAGStrategy
from src.rag.vector_search import VectorSearch
from src.rag.keyword_search import KeywordSearch
from src.rag.hybrid_search import HybridSearch
from src.rag.rrf import reciprocal_rank_fusion
from src.rag.query_expansion import generate_query_variations
from src.rag.context_builder import build_context
from src.rag.prompt_builder import prepare_prompt_and_invoke_llm
from src.schemas.common import Citation


class RAGPipeline:
    """
    Main RAG pipeline orchestrator.
    
    Supports multiple retrieval strategies:
    - basic: Simple vector search
    - hybrid: Vector + Keyword with RRF fusion
    - multi-query-vector: Multiple query variations + vector search
    - multi-query-hybrid: Multiple query variations + hybrid search
    
    Supports multiple LLM providers:
    - openai: GPT-4o-mini
    - ollama: Qwen 2.5 7B (local)
    """
    
    def __init__(self):
        self.vector_search = VectorSearch()
        self.keyword_search = KeywordSearch()
        self.hybrid_search = HybridSearch()
    
    def process(
        self,
        query: str,
        document_ids: List[str],
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the RAG pipeline based on configured strategy.
        
        Args:
            query: User's question
            document_ids: List of document IDs to search
            settings: Project settings dict with RAG configuration
            
        Returns:
            Dict with 'answer', 'citations', and metadata
        """
        strategy = settings.get("rag_strategy", RAGStrategy.BASIC.value)
        llm_provider = settings.get("llm_provider", "openai")
        
        print(f"\n🔍 RAG STRATEGY: {strategy.upper()}")
        print(f"🤖 LLM PROVIDER: {llm_provider.upper()}")
        
        # Step 1: Retrieve chunks based on strategy
        chunks = self._retrieve(query, document_ids, settings, strategy)
        
        # Step 2: Trim to final context size
        final_size = settings.get("final_context_size", 5)
        chunks = chunks[:final_size]
        print(f"📄 Trimmed to final context size: {len(chunks)} chunks")
        
        # Step 3: Build context
        texts, images, tables, citations = build_context(chunks)
        
        # Step 4: Generate response with selected LLM provider
        print(f"🤖 Preparing context and calling LLM ({llm_provider})...")
        ai_response = prepare_prompt_and_invoke_llm(
            user_query=query,
            texts=texts,
            images=images,
            tables=tables,
            llm_provider=llm_provider
        )
        
        return {
            "answer": ai_response,
            "citations": [c.model_dump() for c in citations],
            "chunks": chunks,
            "chunks_used": len(chunks),
            "strategy": strategy,
            "llm_provider": llm_provider
        }
    
    def _retrieve(
        self,
        query: str,
        document_ids: List[str],
        settings: Dict[str, Any],
        strategy: str
    ) -> List[Dict[str, Any]]:
        """Execute retrieval based on strategy."""
        
        if strategy == RAGStrategy.BASIC.value:
            return self._basic_retrieval(query, document_ids, settings)
        
        elif strategy == RAGStrategy.HYBRID.value:
            return self._hybrid_retrieval(query, document_ids, settings)
        
        elif strategy == RAGStrategy.MULTI_QUERY_VECTOR.value:
            return self._multi_query_vector(query, document_ids, settings)
        
        elif strategy == RAGStrategy.MULTI_QUERY_HYBRID.value:
            return self._multi_query_hybrid(query, document_ids, settings)
        
        else:
            print(f"⚠️ Unknown strategy '{strategy}', defaulting to basic")
            return self._basic_retrieval(query, document_ids, settings)
    
    def _basic_retrieval(
        self,
        query: str,
        document_ids: List[str],
        settings: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Basic vector search retrieval."""
        print("📊 Executing: Basic Vector Search")
        
        chunks = self.vector_search.search(
            query=query,
            document_ids=document_ids,
            match_threshold=settings.get("similarity_threshold", 0.3),
            chunks_per_search=settings.get("chunks_per_search", 10)
        )
        print(f"📈 Retrieved {len(chunks)} chunks from vector search")
        
        return chunks
    
    def _hybrid_retrieval(
        self,
        query: str,
        document_ids: List[str],
        settings: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Hybrid search with RRF fusion."""
        print("📊 Executing: Hybrid Search (Vector + Keyword)")
        
        chunks = self.hybrid_search.search(
            query=query,
            document_ids=document_ids,
            match_threshold=settings.get("similarity_threshold", 0.3),
            chunks_per_search=settings.get("chunks_per_search", 10),
            vector_weight=settings.get("vector_weight", 0.7),
            keyword_weight=settings.get("keyword_weight", 0.3)
        )
        print(f"📈 Hybrid search returned {len(chunks)} chunks")
        
        return chunks
    
    def _multi_query_vector(
        self,
        query: str,
        document_ids: List[str],
        settings: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Multi-query with vector search and RRF fusion."""
        num_queries = settings.get("number_of_queries", 3)
        print(f"📊 Executing: Multi-Query Vector Search ({num_queries} queries)")
        
        # Generate query variations
        queries = generate_query_variations(query, num_queries)
        print(f"🔄 Generated queries: {queries}")
        
        # Execute searches for each query
        all_results = []
        for i, q in enumerate(queries):
            results = self.vector_search.search(
                query=q,
                document_ids=document_ids,
                match_threshold=settings.get("similarity_threshold", 0.3),
                chunks_per_search=settings.get("chunks_per_search", 10)
            )
            print(f"📈 Query {i+1} '{q[:50]}...' returned: {len(results)} chunks")
            all_results.append(results)
        
        # Fuse all results with RRF
        chunks = reciprocal_rank_fusion(all_results)
        print(f"🔗 RRF fusion returned: {len(chunks)} unique chunks")
        
        return chunks
    
    def _multi_query_hybrid(
        self,
        query: str,
        document_ids: List[str],
        settings: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Multi-query with hybrid search and RRF fusion."""
        num_queries = settings.get("number_of_queries", 3)
        print(f"📊 Executing: Multi-Query Hybrid Search ({num_queries} queries)")
        
        # Generate query variations
        queries = generate_query_variations(query, num_queries)
        print(f"🔄 Generated queries: {queries}")
        
        # Execute hybrid searches for each query
        all_results = []
        for i, q in enumerate(queries):
            results = self.hybrid_search.search(
                query=q,
                document_ids=document_ids,
                match_threshold=settings.get("similarity_threshold", 0.3),
                chunks_per_search=settings.get("chunks_per_search", 10),
                vector_weight=settings.get("vector_weight", 0.7),
                keyword_weight=settings.get("keyword_weight", 0.3)
            )
            print(f"📈 Query {i+1} '{q[:50]}...' returned: {len(results)} chunks")
            all_results.append(results)
        
        # Fuse all results with RRF
        chunks = reciprocal_rank_fusion(all_results)
        print(f"🔗 RRF fusion returned: {len(chunks)} unique chunks")
        
        return chunks


# Default instance
rag_pipeline = RAGPipeline()