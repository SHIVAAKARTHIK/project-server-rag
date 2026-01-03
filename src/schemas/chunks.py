from pydantic import BaseModel
from typing import Optional,List,Any

class ChunkResponse(BaseModel):
    """Response schema for chunk details."""
    id: str
    document_id: str
    content: str
    chunk_index: int
    page_number: int
    char_count: int
    type: List[str]  
    original_content: Optional[Any] = None 
    filename: str