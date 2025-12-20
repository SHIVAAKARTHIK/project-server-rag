from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser
from src.schemas.chat import ChatCreate, SendMessageRequest
from src.services.database.repositories.chat_repo import ChatRepository, MessageRepository
from src.services.database.repositories.project_repo import ProjectSettingsRepository
from src.services.database.repositories.document_repo import DocumentRepository
from src.rag.pipeline import RAGPipeline

router = APIRouter()

chat_repo = ChatRepository()
message_repo = MessageRepository()
settings_repo = ProjectSettingsRepository()
doc_repo = DocumentRepository()


@router.post("")
async def create_chat(chat_data: ChatCreate, clerk_id: CurrentUser):
    """Create a new chat session."""
    try:
        chat = chat_repo.create({
            "title": chat_data.title,
            "project_id": chat_data.project_id,
            "clerk_id": clerk_id
        })
        
        return {
            "message": "Chat created successfully",
            "data": chat
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat: {str(e)}"
        )


@router.get("/{chat_id}")
async def get_chat(chat_id: str, clerk_id: CurrentUser):
    """Get chat with all messages."""
    chat = chat_repo.get_with_messages(chat_id, clerk_id)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found or access denied"
        )
    
    return {
        "message": "Chat retrieved successfully",
        "data": chat
    }


@router.delete("/{chat_id}")
async def delete_chat(chat_id: str, clerk_id: CurrentUser):
    """Delete a chat and its messages."""
    deleted = chat_repo.delete(chat_id, clerk_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found or access denied"
        )
    
    return {
        "message": "Chat deleted successfully",
        "data": deleted
    }


