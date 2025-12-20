from typing import List, Dict, Any, Optional


def reciprocal_rank_fusion(
    search_results_list: List[List[Dict[str, Any]]],
    weights: Optional[List[float]] = None,
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Combine multiple search result lists using Reciprocal Rank Fusion.
    
    RRF Score formula: Σ weight_i * (1 / (k + rank_i + 1))
    
    Args:
        search_results_list: List of search result lists to fuse
        weights: Optional weights for each result list (defaults to equal)
        k: Ranking constant (default 60, prevents high ranks from dominating)
        
    Returns:
        Fused and sorted results with RRF scores
        
    Example:
        >>> vector_results = [{"id": "a", "score": 0.9}, {"id": "b", "score": 0.8}]
        >>> keyword_results = [{"id": "b", "score": 15}, {"id": "c", "score": 10}]
        >>> fused = reciprocal_rank_fusion(
        ...     [vector_results, keyword_results],
        ...     weights=[0.7, 0.3]
        ... )
    """
    if not search_results_list or not any(search_results_list):
        return []
    
    # Default to equal weights
    if weights is None:
        weights = [1.0 / len(search_results_list)] * len(search_results_list)
    
    chunk_scores: Dict[str, float] = {}
    all_chunks: Dict[str, Dict[str, Any]] = {}
    
    for search_idx, results in enumerate(search_results_list):
        weight = weights[search_idx]
        
        for rank, chunk in enumerate(results):
            chunk_id = chunk.get("id")
            if not chunk_id:
                continue
            
            # RRF score calculation
            rrf_score = weight * (1.0 / (k + rank + 1))
            
            if chunk_id in chunk_scores:
                chunk_scores[chunk_id] += rrf_score
            else:
                chunk_scores[chunk_id] = rrf_score
                all_chunks[chunk_id] = chunk
    
    # Sort by RRF score descending
    sorted_chunk_ids = sorted(
        chunk_scores.keys(),
        key=lambda cid: chunk_scores[cid],
        reverse=True
    )
    
    # Build result list with RRF scores
    return [
        {**all_chunks[chunk_id], "rrf_score": chunk_scores[chunk_id]}
        for chunk_id in sorted_chunk_ids
    ]


def fuse_two_lists(
    vector_results: List[Dict[str, Any]],
    keyword_results: List[Dict[str, Any]],
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3,
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Convenience function to fuse vector and keyword search results.
    
    Args:
        vector_results: Results from vector similarity search
        keyword_results: Results from keyword/BM25 search
        vector_weight: Weight for vector search (default 0.7)
        keyword_weight: Weight for keyword search (default 0.3)
        k: RRF constant
        
    Returns:
        Fused results sorted by RRF score
    """
    return reciprocal_rank_fusion(
        [vector_results, keyword_results],
        [vector_weight, keyword_weight],
        k
    )
