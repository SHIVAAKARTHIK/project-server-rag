from supabase import create_client, Client
from functools import lru_cache

from src.config import settings


@lru_cache
def get_supabase_client() -> Client:
    """
    Get a cached Supabase client instance.
    
    Returns:
        Client: Supabase client instance
        
    Raises:
        ValueError: If Supabase credentials are not configured
    """
    if not settings.SUPABASE_API_URL or not settings.SUPABASE_SERVICE_KEY:
        raise ValueError("SUPABASE_API_URL or SUPABASE_SERVICE_KEY is not set")
    

    return create_client(
        settings.SUPABASE_API_URL,
        settings.SUPABASE_SERVICE_KEY
    )


# Default client instance
supabase = get_supabase_client()
