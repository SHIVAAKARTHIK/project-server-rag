from typing import List, Dict, Any, Tuple

from unstructured.chunking.title import chunk_by_title

from src.models.enums import SourceType, ContentType


class DocumentChunker:
    """Service for chunking document elements."""
    
    DEFAULT_MAX_CHARS = 3000
    DEFAULT_NEW_AFTER_CHARS = 2400
    DEFAULT_COMBINE_UNDER_CHARS = 500
    
    def chunk(
        self,
        elements: List[Any],
        max_characters: int = None,
        new_after_n_chars: int = None,
        combine_text_under_n_chars: int = None
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Chunk elements using title-based strategy.
        
        Args:
            elements: List of unstructured elements
            max_characters: Hard limit for chunk size
            new_after_n_chars: Soft limit to start new chunk
            combine_text_under_n_chars: Threshold to merge small chunks
            
        Returns:
            Tuple of (chunks, metrics)
        """
        chunks = chunk_by_title(
            elements,
            max_characters=max_characters or self.DEFAULT_MAX_CHARS,
            new_after_n_chars=new_after_n_chars or self.DEFAULT_NEW_AFTER_CHARS,
            combine_text_under_n_chars=combine_text_under_n_chars or self.DEFAULT_COMBINE_UNDER_CHARS
        )
        
        metrics = {
            "total_chunks": len(chunks),
            "max_characters": max_characters or self.DEFAULT_MAX_CHARS,
        }
        
        return chunks, metrics
    
    def separate_content_types(
        self,
        chunk: Any,
        source_type: SourceType = SourceType.FILE
    ) -> Dict[str, Any]:
        """
        Separate chunk content by type (text, tables, images).
        
        Args:
            chunk: Unstructured chunk element
            source_type: Source type (file or URL)
            
        Returns:
            Dictionary with separated content
        """
        is_url_source = source_type == SourceType.URL
        
        content_data = {
            "text": chunk.text,
            "tables": [],
            "images": [],
            "types": [ContentType.TEXT.value]
        }
        
        # Check for tables and images in original elements
        if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "orig_elements"):
            for element in chunk.metadata.orig_elements:
                element_type = type(element).__name__
                
                # Handle tables
                if element_type == "Table":
                    content_data["types"].append(ContentType.TABLE.value)
                    table_html = getattr(
                        element.metadata, "text_as_html", element.text
                    )
                    content_data["tables"].append(table_html)
                
                # Handle images (skip for URL sources)
                elif element_type == "Image" and not is_url_source:
                    if hasattr(element, "metadata") and hasattr(element.metadata, "image_base64"):
                        content_data["types"].append(ContentType.IMAGE.value)
                        content_data["images"].append(element.metadata.image_base64)
        
        # Remove duplicate types
        content_data["types"] = list(set(content_data["types"]))
        
        return content_data
    
    @staticmethod
    def get_page_number(chunk: Any, chunk_index: int) -> int:
        """Extract page number from chunk metadata or use fallback."""
        if hasattr(chunk, "metadata"):
            page_number = getattr(chunk.metadata, "page_number", None)
            if page_number is not None:
                return page_number
        
        return chunk_index + 1
