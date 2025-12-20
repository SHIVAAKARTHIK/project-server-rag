from fastapi import APIRouter, HTTPException, Request, status

from src.models.enums import WebhookEventType
from src.core.security import verify_webhook_signature
from src.services.database.repositories.user_repo import UserRepository

router = APIRouter()

user_repo = UserRepository()


@router.post("/clerk")
async def clerk_webhook(request: Request):
    """
    Handle Clerk webhook events.
    
    Supported events:
    - user.created: Create user in database
    - user.updated: Update user (if needed)
    - user.deleted: Delete user (if needed)
    """
    try:
        # Get raw body and headers
        payload = await request.body()
        headers = {
            "svix-id": request.headers.get("svix-id"),
            "svix-timestamp": request.headers.get("svix-timestamp"),
            "svix-signature": request.headers.get("svix-signature"),
        }
        
        # Verify webhook signature
        event = verify_webhook_signature(payload, headers)
        
        event_type = event.get("type")
        data = event.get("data", {})
        
        print(f"📨 Received webhook event: {event_type}")
        
        if event_type == WebhookEventType.USER_CREATED.value:
            clerk_id = data.get("id")
            
            if not clerk_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing user ID in webhook data"
                )
            
            # Check if user already exists
            if user_repo.exists_by_clerk_id(clerk_id):
                return {
                    "message": "User already exists",
                    "data": {"clerk_id": clerk_id}
                }
            
            # Create user
            user = user_repo.create_from_clerk(clerk_id)
            print(f"✅ User created: {clerk_id}")
            
            return {
                "message": "User created successfully",
                "data": user
            }
        
        elif event_type == WebhookEventType.USER_DELETED.value:
            clerk_id = data.get("id")
            print(f"🗑️ User deletion event received: {clerk_id}")
            # Optionally handle user deletion
            # user_repo.delete_by_clerk_id(clerk_id)
            
            return {
                "message": f"User deletion event received",
                "data": {"clerk_id": clerk_id}
            }
        
        # Unhandled event type
        return {
            "message": f"Event {event_type} received but not processed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )
