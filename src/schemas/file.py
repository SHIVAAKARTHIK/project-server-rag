from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.models.enums import ProcessingStatus, SourceType, FileType


class FileUploadRequest(BaseModel):
    """Schema for requesting a file upload URL."""
    filename: str = Field(..., min_length=1, max_length=255)
    file_size: int = Field(..., gt=0)
    file_type: str


class FileUploadResponse(BaseModel):
    """Schema for file upload URL response."""
    upload_url: str
    s3_key: str
    document: "DocumentResponse"


class FileConfirmRequest(BaseModel):
    """Schema for confirming file upload."""
    s3_key: str = Field(..., min_length=1)


class UrlRequest(BaseModel):
    """Schema for URL processing request."""
    url: str = Field(..., description="The URL to process")


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: str
    project_id: str
    filename: str
    s3_key: Optional[str] = None
    file_size: int
    file_type: str
    processing_status: ProcessingStatus
    processing_details: Optional[Dict[str, Any]] = None
    source_type: SourceType = SourceType.FILE
    source_url: Optional[str] = None
    task_id: Optional[str] = None
    clerk_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentChunkResponse(BaseModel):
    """Schema for document chunk response."""
    id: str
    document_id: str
    chunk_index: int
    content: str
    original_content: Optional[Dict[str, Any]] = None
    type: Optional[List[str]] = None
    page_number: Optional[int] = None
    char_count: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProcessingDetails(BaseModel):
    """Schema for document processing details."""
    partitioning: Optional[Dict[str, Any]] = None
    chunking: Optional[Dict[str, Any]] = None
    summarizing: Optional[Dict[str, Any]] = None
