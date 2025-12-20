from enum import Enum


class ProcessingStatus(str, Enum):
    """Document processing status states."""
    UPLOADING = "uploading"
    QUEUED = "queued"
    PARTITIONING = "partitioning"
    CHUNKING = "chunking"
    SUMMARIZING = "summarising"
    VECTORIZATION = "vectorization"
    COMPLETED = "completed"
    FAILED = "failed"


class RAGStrategy(str, Enum):
    """Available RAG retrieval strategies."""
    BASIC = "basic"                      # Simple vector search
    HYBRID = "hybrid"                    # Vector + Keyword search with RRF
    MULTI_QUERY_VECTOR = "multi-query-vector"    # Multiple query variations + vector
    MULTI_QUERY_HYBRID = "multi-query-hybrid"    # Multiple query variations + hybrid


class AgentType(str, Enum):
    """Agent behavior types."""
    AGENTIC = "agentic"
    CONVERSATIONAL = "conversational"
    RETRIEVAL_ONLY = "retrieval_only"


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SourceType(str, Enum):
    """Document source types."""
    FILE = "file"
    URL = "url"


class EmbeddingModel(str, Enum):
    """Available embedding models."""
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"


class RerankingModel(str, Enum):
    """Available reranking models."""
    RERANKER_ENGLISH_V3 = "reranker-english-v3.0"
    RERANKER_MULTILINGUAL_V3 = "reranker-multilingual-v3.0"
    NONE = "none"


class FileType(str, Enum):
    """Supported file types for processing."""
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TXT = "txt"
    MD = "md"
    HTML = "html"


class ContentType(str, Enum):
    """Content types within document chunks."""
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    TITLE = "title"


class WebhookEventType(str, Enum):
    """Clerk webhook event types."""
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
