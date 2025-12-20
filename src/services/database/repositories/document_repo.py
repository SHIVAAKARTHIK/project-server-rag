from typing import Optional, Dict, Any, List

from src.services.database.repositories.base import BaseRepository
from src.models.enums import ProcessingStatus


class DocumentRepository(BaseRepository):
    """Repository for document operations."""
    
    def __init__(self):
        super().__init__("project_documents")
    
    def get_by_project(
        self,
        project_id: str,
        clerk_id: str
    ) -> List[Dict[str, Any]]:
        """Get all documents for a project."""
        return self.get_all(
            clerk_id=clerk_id,
            filters={"project_id": project_id},
            order_by="created_at",
            desc=True
        )
    
    def get_document_ids(self, project_id: str) -> List[str]:
        """Get all document IDs for a project."""
        result = self.db.table(self.table_name)\
            .select("id")\
            .eq("project_id", project_id)\
            .execute()
        
        return [doc["id"] for doc in result.data] if result.data else [] 
    
    def update_status(
        self,
        document_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update document processing status with details."""
        # Get current details
        result = self.db.table(self.table_name)\
            .select("processing_details")\
            .eq("id", document_id)\
            .execute()
        
        current_details = {}
        if result.data and result.data[0].get("processing_details"):
            current_details = result.data[0]["processing_details"]
        
        if details:
            current_details.update(details) 
        
        # Update status and details
        update_data = {
            "processing_status": status.value if isinstance(status, ProcessingStatus) else status,
            "processing_details": current_details
        }
        
        return self.update(document_id, update_data)
    
    def update_task_id(self, document_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Update the Celery task ID for a document."""
        return self.update(document_id, {"task_id": task_id})


class DocumentChunkRepository(BaseRepository):
    """Repository for document chunk operations."""
    
    def __init__(self):
        super().__init__("document_chunks")
    
    def get_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a document."""
        result = self.db.table(self.table_name)\
            .select("*")\
            .eq("document_id", document_id)\
            .order("chunk_index")\
            .execute()
        
        return result.data or []
    
    def insert_chunk(self, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a single chunk."""
        return self.create(chunk_data)
    
    def insert_chunks_batch(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple chunks in batch."""
        stored_ids = []
        
        for chunk in chunks:
            result = self.create(chunk)
            stored_ids.append(result["id"])
        
        return stored_ids
    
    def delete_by_document(self, document_id: str) -> int:
        """Delete all chunks for a document."""
        result = self.db.table(self.table_name)\
            .delete()\
            .eq("document_id", document_id)\
            .execute()
        
        return len(result.data) if result.data else 0
