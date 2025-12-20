from typing import TypeVar, Generic, Optional, List, Dict, Any
from abc import ABC

from src.services.database.supabase import supabase



class BaseRepository(ABC):
    """Base repository with common CRUD operations."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = supabase
    
    def get_by_id(self, id: str, clerk_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a record by ID, optionally filtered by clerk_id."""
        query = self.db.table(self.table_name).select("*").eq("id", id)
        
        if clerk_id:
            query = query.eq("clerk_id", clerk_id)
        
        result = query.execute()
        return result.data[0] if result.data else None  # type: ignore
    
    def get_all(
        self,
        clerk_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        desc: bool = True,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all records with optional filters."""
        query = self.db.table(self.table_name).select("*")
        
        if clerk_id:
            query = query.eq("clerk_id", clerk_id)
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        if order_by:
            query = query.order(order_by, desc=desc)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        return result.data or [] # type: ignore
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record."""
        result = self.db.table(self.table_name).insert(data).execute()
        
        if not result.data:
            raise Exception(f"Failed to create record in {self.table_name}")
        
        return result.data[0] # type: ignore
    
    def update(
        self,
        id: str,
        data: Dict[str, Any],
        clerk_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a record by ID."""
        query = self.db.table(self.table_name).update(data).eq("id", id)
        
        if clerk_id:
            query = query.eq("clerk_id", clerk_id)
        
        result = query.execute()
        return result.data[0] if result.data else None # type: ignore
    
    def delete(self, id: str, clerk_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Delete a record by ID."""
        query = self.db.table(self.table_name).delete().eq("id", id)
        
        if clerk_id:
            query = query.eq("clerk_id", clerk_id)
        
        result = query.execute()
        return result.data[0] if result.data else None # type: ignore
    
    def exists(self, id: str, clerk_id: Optional[str] = None) -> bool:
        """Check if a record exists."""
        return self.get_by_id(id, clerk_id) is not None
