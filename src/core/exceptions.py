from fastapi import HTTPException, status
from typing import Optional, Any, Dict


class BaseAppException(HTTPException):
    """Base exception for application errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class NotFoundException(BaseAppException):
    """Resource not found exception."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found: {identifier}",
            error_code="NOT_FOUND"
        )


class AccessDeniedException(BaseAppException):
    """Access denied exception."""
    
    def __init__(self, resource: str = "resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to {resource}",
            error_code="ACCESS_DENIED"
        )


class ValidationException(BaseAppException):
    """Validation error exception."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )


class DatabaseException(BaseAppException):
    """Database operation exception."""
    
    def __init__(self, operation: str, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database {operation} failed: {detail}",
            error_code="DATABASE_ERROR"
        )


class ExternalServiceException(BaseAppException):
    """External service error exception."""
    
    def __init__(self, service: str, detail: str):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{service} service error: {detail}",
            error_code="EXTERNAL_SERVICE_ERROR"
        )


class DocumentProcessingException(BaseAppException):
    """Document processing error exception."""
    
    def __init__(self, document_id: str, stage: str, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document {document_id} failed at {stage}: {detail}",
            error_code="DOCUMENT_PROCESSING_ERROR"
        )


class RAGException(BaseAppException):
    """RAG pipeline error exception."""
    
    def __init__(self, stage: str, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG {stage} failed: {detail}",
            error_code="RAG_ERROR"
        )
