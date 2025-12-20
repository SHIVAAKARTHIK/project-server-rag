import json
from typing import Any, Optional

import redis

from src.config import settings


class RedisService:
    """Service for Redis cache operations."""
    
    def __init__(self, url: Optional[str] = None):
        self.url = url or settings.REDIS_URL
        self._client: Optional[redis.Redis] = None  # type: ignore
    
    @property
    def client(self) -> redis.Redis:  # type: ignore
        """Lazy-loaded Redis client."""
        if self._client is None:
            self._client = redis.from_url(self.url, decode_responses=True)
        return self._client
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)  # type: ignore
            except json.JSONDecodeError:
                return value
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional expiration."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        return bool(self.client.set(key, value, ex=expire))
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        return bool(self.client.delete(key))
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return bool(self.client.exists(key))
    
    def set_hash(self, name: str, mapping: dict) -> bool:
        """Set hash values."""
        return bool(self.client.hset(name, mapping=mapping))  # type: ignore
    
    def ping(self) -> bool:
        """Check Redis connection."""
        try:
            return bool(self.client.ping())
        except Exception:
            return False


# Default instance
redis_service = RedisService()