from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from src.models.enums import WebhookEventType


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    clerk_id: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    clerk_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClerkWebhookPayload(BaseModel):
    """Schema for Clerk webhook payload."""
    type: WebhookEventType
    data: Dict[str, Any]


class WebhookHeaders(BaseModel):
    """Schema for Svix webhook headers."""
    svix_id: str
    svix_timestamp: str
    svix_signature: str
