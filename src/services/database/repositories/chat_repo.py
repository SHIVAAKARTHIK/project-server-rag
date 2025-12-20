from typing import Optional, Dict, Any, List

from src.services.database.repositories.base import BaseRepository
from src.models.enums import MessageRole


class ChatRepository(BaseRepository):
    """Repository for chat operations."""
    
    def __init__(self):
        super().__init__("chats")
    
    def get_by_project(
        self,
        project_id: str,
        clerk_id: str
    ) -> List[Dict[str, Any]]:
        """Get all chats for a project."""
        return self.get_all(
            clerk_id=clerk_id,
            filters={"project_id": project_id},
            order_by="created_at",
            desc=True
        )
    
    def get_with_messages(
        self,
        chat_id: str,
        clerk_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get chat with all its messages."""
        chat = self.get_by_id(chat_id, clerk_id)
        
        if not chat:
            return None
        
        messages_result = self.db.table("messages")\
            .select("*")\
            .eq("chat_id", chat_id)\
            .order("created_at", desc=False)\
            .execute()
        
        chat["messages"] = messages_result.data or []
        return chat


class MessageRepository(BaseRepository):
    """Repository for message operations."""
    
    def __init__(self):
        super().__init__("messages")
    
    def get_by_chat(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a chat."""
        result = self.db.table(self.table_name)\
            .select("*")\
            .eq("chat_id", chat_id)\
            .order("created_at", desc=False)\
            .execute()
        
        return result.data or [] # type: ignore
    
    def create_user_message(
        self,
        chat_id: str,
        content: str,
        clerk_id: str
    ) -> Dict[str, Any]:
        """Create a user message."""
        return self.create({
            "chat_id": chat_id,
            "content": content,
            "role": MessageRole.USER.value,
            "clerk_id": clerk_id
        })
    
    def create_assistant_message(
        self,
        chat_id: str,
        content: str,
        clerk_id: str,
        citations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create an assistant message with optional citations."""
        return self.create({
            "chat_id": chat_id,
            "content": content,
            "role": MessageRole.ASSISTANT.value,
            "clerk_id": clerk_id,
            "citations": citations or []
        })
