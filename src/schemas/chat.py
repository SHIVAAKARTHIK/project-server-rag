from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime

from src.models.enums import MessageRole
from src.schemas.common import Citation


class ChatCreate(BaseModel):
    """Schema for creating a new chat."""
    title: str = Field(..., min_length=1, max_length=255)
    project_id: str


class ChatResponse(BaseModel):
    """Schema for chat response."""
    id: str
    title: str
    project_id: str
    clerk_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: Optional[List["MessageResponse"]] = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: str
    chat_id: str
    content: str
    role: MessageRole
    clerk_id: str
    citations: Optional[List[Citation]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    """Schema for send message API request."""
    content: str = Field(..., min_length=1)


class SendMessageResponse(BaseModel):
    """Schema for send message API response."""
    user_message: MessageResponse
    ai_message: MessageResponse


class RAGContext(BaseModel):
    """Schema for RAG context data."""
    texts: List[str] = []
    images: List[str] = []
    tables: List[str] = []
    citations: List[Citation] = []


class QueryVariations(BaseModel):
    """Schema for LLM-generated query variations."""
    queries: List[str]
