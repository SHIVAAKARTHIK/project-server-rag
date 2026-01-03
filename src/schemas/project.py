from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from src.models.enums import RAGStrategy, AgentType, EmbeddingModel, RerankingModel, LLMProvider


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: str
    name: str
    description: Optional[str] = None
    clerk_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectSettingsCreate(BaseModel):
    """Schema for creating project settings."""
    project_id: str
    embedding_model: EmbeddingModel = EmbeddingModel.TEXT_EMBEDDING_3_LARGE
    rag_strategy: RAGStrategy = RAGStrategy.BASIC
    agent_type: AgentType = AgentType.AGENTIC
    chunks_per_search: int = Field(default=10, ge=1, le=50)
    final_context_size: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    number_of_queries: int = Field(default=5, ge=1, le=10)
    reranking_enabled: bool = True
    reranking_model: RerankingModel = RerankingModel.RERANKER_ENGLISH_V3
    vector_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    keyword_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    llm_provider: LLMProvider = LLMProvider.OPENAI


class ProjectSettingsUpdate(BaseModel):
    """Schema for updating project settings."""
    embedding_model: Optional[EmbeddingModel] = None
    rag_strategy: Optional[RAGStrategy] = None
    agent_type: Optional[AgentType] = None
    chunks_per_search: Optional[int] = Field(None, ge=1, le=50)
    final_context_size: Optional[int] = Field(None, ge=1, le=20)
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    number_of_queries: Optional[int] = Field(None, ge=1, le=10)
    reranking_enabled: Optional[bool] = None
    reranking_model: Optional[RerankingModel] = None
    vector_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    keyword_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    llm_provider: Optional[LLMProvider] = None


class ProjectSettingsResponse(BaseModel):
    """Schema for project settings response."""
    id: str
    project_id: str
    embedding_model: str
    rag_strategy: str
    agent_type: str
    chunks_per_search: int
    final_context_size: int
    similarity_threshold: float
    number_of_queries: int
    reranking_enabled: bool
    reranking_model: str
    vector_weight: float
    keyword_weight: float
    llm_provider: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True