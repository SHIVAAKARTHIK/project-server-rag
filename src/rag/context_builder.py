from typing import List, Dict, Any, Tuple

from src.services.database.supabase import supabase
from src.schemas.common import Citation


def build_context(
    chunks: List[Dict[str, Any]]
) -> Tuple[List[str], List[str], List[str], List[Citation]]:
    """
    Build RAG context from retrieved chunks.
    
    Extracts text, images, tables, and generates citations from chunks.
    
    Args:
        chunks: List of document chunks from search
        
    Returns:
        Tuple of (texts, images, tables, citations)
        
    Example:
        >>> texts, images, tables, citations = build_context(search_results)
        >>> print(f"Found {len(texts)} text chunks, {len(images)} images")
    """
    texts: List[str] = []
    images: List[str] = []
    tables: List[str] = []
    citations: List[Citation] = []
    
    # Get unique document IDs to fetch filenames
    doc_ids = [
        chunk["document_id"] 
        for chunk in chunks 
        if chunk.get("document_id")
    ]
    unique_doc_ids = list(set(doc_ids))
    
    # Fetch document filenames
    filename_map: Dict[str, str] = {}
    if unique_doc_ids:
        result = supabase.table("project_documents")\
            .select("id", "filename")\
            .in_("id", unique_doc_ids)\
            .execute()
        
        filename_map = {
            doc["id"]: doc["filename"] 
            for doc in result.data
        }
    
    # Process each chunk
    for chunk in chunks:
        original_content = chunk.get("original_content", {})
        
        # Extract content by type
        chunk_text = original_content.get("text", "")
        chunk_images = original_content.get("images", [])
        chunk_tables = original_content.get("tables", [])
        
        # Collect content
        if chunk_text:
            texts.append(chunk_text)
        images.extend(chunk_images)
        tables.extend(chunk_tables)
        
        # Build citation
        doc_id = chunk.get("document_id")
        if doc_id:
            citation = Citation(
                chunk_id=chunk.get("id", ""),
                document_id=doc_id,
                filename=filename_map.get(doc_id, "Unknown Document"),
                page=chunk.get("page_number")
            )
            citations.append(citation)
    
    return texts, images, tables, citations


def format_context_for_prompt(
    texts: List[str],
    tables: List[str],
    images: List[str]
) -> str:
    """
    Format context into a string for the system prompt.
    
    Args:
        texts: List of text chunks
        tables: List of HTML table strings
        images: List of base64 images (for reference counting)
        
    Returns:
        Formatted context string
    """
    parts = []
    
    # Add text context
    if texts:
        parts.append("=" * 80)
        parts.append("CONTEXT DOCUMENTS")
        parts.append("=" * 80 + "\n")
        
        for i, text in enumerate(texts, 1):
            parts.append(f"--- Document Chunk {i} ---")
            parts.append(text.strip())
            parts.append("")
    
    # Add tables
    if tables:
        parts.append("\n" + "=" * 80)
        parts.append("RELATED TABLES")
        parts.append("=" * 80)
        parts.append(
            "The following tables contain structured data. "
            "Analyze the table contents carefully.\n"
        )
        
        for i, table_html in enumerate(tables, 1):
            parts.append(f"--- Table {i} ---")
            parts.append(table_html)
            parts.append("")
    
    # Reference images
    if images:
        parts.append("\n" + "=" * 80)
        parts.append("RELATED IMAGES")
        parts.append("=" * 80)
        parts.append(
            f"{len(images)} image(s) will be provided alongside the user's question. "
            "Analyze the visual content when formulating your response.\n"
        )
    
    return "\n".join(parts)
