from typing import Optional, Dict, Any

from src.services.database.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for user operations."""
    
    def __init__(self):
        super().__init__("users")
    
    def get_by_clerk_id(self, clerk_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Clerk ID."""
        result = self.db.table(self.table_name)\
            .select("*")\
            .eq("clerk_id", clerk_id)\
            .execute()
        
        return result.data[0] if result.data else None
    
    def create_from_clerk(self, clerk_id: str) -> Dict[str, Any]:
        """Create a new user from Clerk webhook."""
        return self.create({"clerk_id": clerk_id})
    
    def exists_by_clerk_id(self, clerk_id: str) -> bool:
        """Check if user exists by Clerk ID."""
        return self.get_by_clerk_id(clerk_id) is not None
