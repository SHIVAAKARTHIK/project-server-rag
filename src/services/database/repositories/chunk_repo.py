from typing import Optional, Dict, Any
from src.services.database.repositories.base import BaseRepository


class ChunkRepository(BaseRepository):
    """Repository for document_chunks table operations."""
    
    def __init__(self):
        super().__init__("document_chunks")
    
    def get_chunk_with_document(
        self,
        chunk_id: str,
        clerk_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get chunk details with associated document info.
        
        Joins with documents table to get filename and verify ownership.
        
        Args:
            chunk_id: The chunk ID to fetch
            clerk_id: User's clerk ID for access verification
            
        Returns:
            Chunk data with document info, or None if not found/unauthorized
        """
        result = self.db.table(self.table_name) \
            .select("""
                id,
                document_id,
                content,
                chunk_index,
                page_number,
                char_count,
                type,
                original_content,
                project_documents!inner(filename, clerk_id)
            """) \
            .eq("id", chunk_id) \
            .single() \
            .execute()
        
        if not result.data:
            return None
        
        chunk = result.data
        
        # Verify user owns this document
        if chunk["project_documents"]["clerk_id"] != clerk_id:
            return None
        
        return chunk
    
    def get_chunks_by_document(
        self,
        document_id: str,
        clerk_id: str
    ) -> list[Dict[str, Any]]:
        """
        Get all chunks for a document.
        
        Args:
            document_id: The document ID
            clerk_id: User's clerk ID for access verification
            
        Returns:
            List of chunks ordered by chunk_index
        """
        result = self.db.table(self.table_name) \
            .select("""
                id,
                document_id,
                content,
                chunk_index,
                page_number,
                char_count,
                type,
                original_content,
                project_documents!inner(clerk_id)
            """) \
            .eq("document_id", document_id) \
            .order("chunk_index", desc=False) \
            .execute()
        
        if not result.data:
            return []
        
        # Filter by clerk_id (document ownership)
        chunks = [
            chunk for chunk in result.data
            if chunk["project_documents"]["clerk_id"] == clerk_id
        ]
        
        return chunks


# Singleton instance
chunk_repo = ChunkRepository()