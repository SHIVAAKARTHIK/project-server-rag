from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser
from src.schemas.chat import SendMessageRequest
from src.services.database.repositories.chat_repo import MessageRepository
from src.services.database.repositories.project_repo import ProjectSettingsRepository
from src.services.database.repositories.document_repo import DocumentRepository
from src.rag.pipeline import RAGPipeline

router = APIRouter()

message_repo = MessageRepository()
settings_repo = ProjectSettingsRepository()
doc_repo = DocumentRepository()


@router.post("/{project_id}/chats/{chat_id}/messages")
async def send_message(
    project_id: str,
    chat_id: str,
    request: SendMessageRequest,
    clerk_id: CurrentUser
):
    """
    Send a message and get RAG-powered response.
    """
    try:
        message = request.content
        print(f"💬 New message: {message[:50]}...")
        
        # 1. Save user message
        print("💾 Saving user message...")
        user_message = message_repo.create_user_message(
            chat_id=chat_id,
            content=message,
            clerk_id=clerk_id
        )
        print(f"✅ User message saved: {user_message['id']}")
        
        # 2. Load project settings
        settings = settings_repo.get_by_project_id(project_id)
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project settings not found"
            )
        
        # 3. Get document IDs
        document_ids = doc_repo.get_document_ids(project_id)
        print(f"📄 Found {len(document_ids)} documents")
        
        # 4. Execute RAG pipeline
        rag = RAGPipeline()
        result = rag.process(
            query=message,
            document_ids=document_ids,
            settings=settings
        )
        
        # 5. Save AI response
        print("💾 Saving AI message...")
        ai_message = message_repo.create_assistant_message(
            chat_id=chat_id,
            content=result["answer"],
            clerk_id=clerk_id,
            citations=result["citations"]
        )
        print(f"✅ AI message saved: {ai_message['id']}")
        
        return {
            "message": "Messages sent successfully",
            "data": {
                "userMessage": user_message,
                "aiMessage": ai_message
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in send_message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )