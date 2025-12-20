"""Unit tests for RAG components."""

import pytest

from src.rag.rrf import reciprocal_rank_fusion, fuse_two_lists


class TestRRF:
    """Tests for Reciprocal Rank Fusion."""
    
    def test_rrf_empty_input(self):
        """Test RRF with empty input."""
        result = reciprocal_rank_fusion([])
        assert result == []
    
    def test_rrf_single_list(self):
        """Test RRF with single result list."""
        results = [
            [{"id": "a", "score": 0.9}, {"id": "b", "score": 0.8}]
        ]
        fused = reciprocal_rank_fusion(results)
        
        assert len(fused) == 2
        assert fused[0]["id"] == "a"
        assert fused[1]["id"] == "b"
    
    def test_rrf_fusion(self):
        """Test RRF fusion of two result lists."""
        vector_results = [
            {"id": "a", "score": 0.9},
            {"id": "b", "score": 0.8},
        ]
        keyword_results = [
            {"id": "b", "score": 15},
            {"id": "c", "score": 10},
        ]
        
        fused = fuse_two_lists(
            vector_results,
            keyword_results,
            vector_weight=0.7,
            keyword_weight=0.3
        )
        
        # 'b' should rank highest as it appears in both lists
        assert fused[0]["id"] == "b"
        assert len(fused) == 3
        assert all("rrf_score" in item for item in fused)
    
    def test_rrf_deduplication(self):
        """Test that RRF correctly deduplicates."""
        results = [
            [{"id": "a", "score": 0.9}],
            [{"id": "a", "score": 15}],  # Same doc in both lists
        ]
        
        fused = reciprocal_rank_fusion(results)
        
        # Should only have one 'a'
        assert len(fused) == 1
        assert fused[0]["id"] == "a"


class TestEnums:
    """Tests for enum values."""
    
    def test_processing_status_values(self):
        """Test ProcessingStatus enum values."""
        from src.models.enums import ProcessingStatus
        
        assert ProcessingStatus.UPLOADING.value == "uploading"
        assert ProcessingStatus.COMPLETED.value == "completed"
        assert ProcessingStatus.FAILED.value == "failed"
    
    def test_rag_strategy_values(self):
        """Test RAGStrategy enum values."""
        from src.models.enums import RAGStrategy
        
        assert RAGStrategy.BASIC.value == "basic"
        assert RAGStrategy.HYBRID.value == "hybrid"
        assert RAGStrategy.MULTI_QUERY_HYBRID.value == "multi-query-hybrid"
