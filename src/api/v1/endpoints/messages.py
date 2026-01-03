from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser
from src.schemas.chat import SendMessageRequest
from src.services.database.repositories.chat_repo import MessageRepository
from src.services.database.repositories.project_repo import ProjectSettingsRepository
from src.services.database.repositories.document_repo import DocumentRepository
from src.agents import run_simple_agent

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
    Send a message and get AI-powered response.
    
    Uses the Simple Agent which:
    - Responds directly to greetings and general questions
    - Searches documents when needed
    - Maintains conversation context
    """
    try:
        message = request.content
        print(f"\n💬 New message: {message[:50]}...")
        
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
        
        # 3. Get LLM provider from settings (default to openai)
        llm_provider = settings.get("llm_provider", "openai")
        print(f"🤖 Using LLM provider: {llm_provider}")

        # 4. Get document IDs
        document_ids = doc_repo.get_document_ids(project_id)
        print(f"📄 Found {len(document_ids)} documents")

        # 5. Load chat history for context
        chat_history = _load_chat_history(chat_id)
        print(f"💬 Loaded {len(chat_history)} history messages")

        # 6. Run the Simple Agent
        print("🤖 Running Simple Agent...")
        result = run_simple_agent(
            query=message,
            chat_history=chat_history,
            document_ids=document_ids,
            settings=settings
        )
        print(f"✅ Agent response received (tool_used: {result.tool_used})")
        
        # 7. Save AI response
        print("💾 Saving AI message...")
        ai_message = message_repo.create_assistant_message(
            chat_id=chat_id,
            content=result.response,
            clerk_id=clerk_id,
            citations=result.citations
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
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def _load_chat_history(chat_id: str, limit: int = 10) -> list:
    """
    Load recent chat history for context.
    
    Converts database messages to the format expected by the agent:
    [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    
    Args:
        chat_id: Chat ID to load history for
        limit: Maximum number of messages to load
        
    Returns:
        List of message dicts with role and content
    """
    try:
        # Get recent messages from database
        messages = message_repo.get_by_chat_id(chat_id, limit=limit)
        # Convert to agent format
        chat_history = []
        for msg in messages:
            chat_history.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        return chat_history
        
    except Exception as e:
        print(f"⚠️ Error loading chat history: {str(e)}")
        return []