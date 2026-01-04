"""
Streaming Messages Endpoint with Guardrails Support

Place at: src/api/v1/endpoints/streaming.py
"""

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.api.deps import CurrentUser
from src.services.database.repositories.chat_repo import MessageRepository
from src.services.database.repositories.project_repo import ProjectSettingsRepository
from src.services.database.repositories.document_repo import DocumentRepository
from src.agents.graphs.streaming_agent import stream_agentic_agent

router = APIRouter()

message_repo = MessageRepository()
settings_repo = ProjectSettingsRepository()
doc_repo = DocumentRepository()


class StreamMessageRequest(BaseModel):
    content: str


@router.post("/{project_id}/chats/{chat_id}/messages/stream")
async def stream_message(
    project_id: str,
    chat_id: str,
    request: StreamMessageRequest,
    clerk_id: CurrentUser
):
    """Stream AI response with guardrails."""
    try:
        message = request.content
        print(f"\n💬 [STREAM] New message: {message[:50]}...")
        
        # 1. Save user message
        user_message = message_repo.create_user_message(
            chat_id=chat_id,
            content=message,
            clerk_id=clerk_id
        )
        print(f"✅ User message saved: {user_message['id']}")
        
        # 2. Load settings
        settings = settings_repo.get_by_project_id(project_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Project settings not found")
        
        # 3. Get document IDs
        document_ids = doc_repo.get_document_ids(project_id)
        
        # 4. Load chat history
        chat_history = _load_chat_history(chat_id)
        
        # 5. Stream response
        async def generate_events():
            full_response = ""
            citations = []
            was_blocked = False
            block_message = ""
            
            try:
                # Send user message first
                yield format_sse_event({
                    "type": "user_message",
                    "content": user_message
                })
                
                # Stream from agent
                async for event in stream_agentic_agent(
                    query=message,
                    chat_history=chat_history,
                    document_ids=document_ids,
                    settings=settings
                ):
                    event_type = event.get("type")
                    content = event.get("content", "")
                    
                    # Collect data
                    if event_type == "token":
                        full_response += content
                    elif event_type == "citations":
                        citations = content
                    elif event_type == "guardrail_blocked":
                        # Message was blocked by guardrails
                        was_blocked = True
                        block_message = content
                        full_response = content  # Use block message as response
                        print(f"🚫 Guardrail blocked: {content}")
                    
                    # Forward event to frontend
                    yield format_sse_event(event)
                
                # Save AI message (even if blocked - save the block message)
                ai_message = message_repo.create_assistant_message(
                    chat_id=chat_id,
                    content=full_response if full_response else "I couldn't process that request.",
                    clerk_id=clerk_id,
                    citations=citations if not was_blocked else []
                )
                print(f"✅ AI message saved: {ai_message['id']}")
                
                # Send AI message to frontend
                yield format_sse_event({
                    "type": "ai_message",
                    "content": ai_message
                })
                
            except Exception as e:
                print(f"❌ Stream error: {str(e)}")
                import traceback
                traceback.print_exc()
                yield format_sse_event({
                    "type": "error",
                    "content": str(e)
                })
        
        return StreamingResponse(
            generate_events(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def format_sse_event(data: dict) -> str:
    """Format as SSE event."""
    return f"data: {json.dumps(data)}\n\n"


def _load_chat_history(chat_id: str, limit: int = 10) -> list:
    """Load chat history."""
    try:
        messages = message_repo.get_by_chat_id(chat_id, limit=limit)
        return [
            {"role": msg.get("role"), "content": msg.get("content", "")}
            for msg in messages
        ]
    except:
        return []