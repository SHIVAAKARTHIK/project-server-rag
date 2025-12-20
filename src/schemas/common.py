from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List, Any
from datetime import datetime

T = TypeVar("T")


class ResponseBase(BaseModel):
    """Base response model."""
    message: str


class DataResponse(ResponseBase, Generic[T]):
    """Generic response with data."""
    data: T


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    error_code: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = 1
    page_size: int = 20
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(ResponseBase, Generic[T]):
    """Paginated response model."""
    data: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Citation(BaseModel):
    """Citation model for RAG responses."""
    chunk_id: str
    document_id: str
    filename: str
    page: Optional[int] = None
