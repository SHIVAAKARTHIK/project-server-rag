from typing import Optional, Dict, Any, List

from src.services.database.repositories.base import BaseRepository
from src.models.enums import RAGStrategy, AgentType, EmbeddingModel, RerankingModel


class ProjectRepository(BaseRepository):
    """Repository for project operations."""
    
    def __init__(self):
        super().__init__("projects")
    
    def get_with_settings(self, project_id: str, clerk_id: str) -> Optional[Dict[str, Any]]:
        """Get project with its settings."""
        project = self.get_by_id(project_id, clerk_id)
        
        if not project:
            return None
        
        settings_result = self.db.table("project_settings")\
            .select("*")\
            .eq("project_id", project_id)\
            .execute()
        
        project["settings"] = settings_result.data[0] if settings_result.data else None
        return project


class ProjectSettingsRepository(BaseRepository):
    """Repository for project settings operations."""
    
    def __init__(self):
        super().__init__("project_settings")
    
    def get_by_project_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get settings by project ID."""
        result = self.db.table(self.table_name)\
            .select("*")\
            .eq("project_id", project_id)\
            .execute()
        
        return result.data[0] if result.data else None
    
    def create_default(self, project_id: str) -> Dict[str, Any]:
        """Create default settings for a project."""
        default_settings = {
            "project_id": project_id,
            "embedding_model": EmbeddingModel.TEXT_EMBEDDING_3_LARGE.value,
            "rag_strategy": RAGStrategy.BASIC.value,
            "agent_type": AgentType.AGENTIC.value,
            "chunks_per_search": 10,
            "final_context_size": 5,
            "similarity_threshold": 0.3,
            "number_of_queries": 5,
            "reranking_enabled": True,
            "reranking_model": RerankingModel.RERANKER_ENGLISH_V3.value,
            "vector_weight": 0.7,
            "keyword_weight": 0.3,
        }
        
        return self.create(default_settings)
    
    def update_by_project_id(
        self,
        project_id: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update settings by project ID."""
        result = self.db.table(self.table_name)\
            .update(data)\
            .eq("project_id", project_id)\
            .execute()
        
        return result.data[0] if result.data else None
