import os
from fastapi import Request, HTTPException, status
from clerk_backend_api import AuthenticateRequestOptions, Clerk
from svix.webhooks import Webhook, WebhookVerificationError

from src.config import settings


# Initialize Clerk client
clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)


async def get_current_user(request: Request) -> str:
    """
    Verify Clerk JWT token and return the clerk_id.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: The clerk_id of the authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        request_state = clerk_client.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties=settings.cors_origins
            )
        )
        
        if not request_state.is_signed_in:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        clerk_id = request_state.payload.get("sub")
        
        if not clerk_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        return clerk_id
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


def verify_webhook_signature(payload: bytes, headers: dict) -> dict:
    """
    Verify Clerk webhook signature using Svix.
    
    Args:
        payload: Raw request body bytes
        headers: Dictionary containing svix headers
        
    Returns:
        dict: Verified webhook event data
        
    Raises:
        HTTPException: If signature verification fails
    """
    wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
    
    try:
        event = wh.verify(payload, headers)
        return event
    except WebhookVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
