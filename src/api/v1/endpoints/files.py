from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser
from src.schemas.file import (
    FileUploadRequest,
    FileConfirmRequest,
    UrlRequest,
    DocumentResponse,
)
from src.models.enums import ProcessingStatus, SourceType
from src.services.database.supabase import supabase
from src.services.database.repositories.project_repo import ProjectRepository
from src.services.database.repositories.document_repo import (
    DocumentRepository,
    DocumentChunkRepository,
)
from src.services.storage.s3 import S3Service
from src.tasks.celery_app import celery_app

router = APIRouter()

project_repo = ProjectRepository()
doc_repo = DocumentRepository()
chunk_repo = DocumentChunkRepository()


@router.get("/{project_id}/files")
async def get_project_files(project_id: str, clerk_id: CurrentUser):
    """Get all files for a project."""
    files = doc_repo.get_by_project(project_id, clerk_id)
    
    return {
        "message": "Project files retrieved successfully",
        "data": files
    }


@router.post("/{project_id}/files/upload-url")
async def get_upload_url(
    project_id: str,
    file_request: FileUploadRequest,
    clerk_id: CurrentUser
):
    """Generate presigned URL for file upload."""
    # Verify project access
    if not project_repo.exists(project_id, clerk_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    try:
        # Generate presigned URL
        s3_client = S3Service()
        presigned_url, s3_key = s3_client.generate_upload_url(
            file_name=file_request.filename,
            file_type=file_request.file_type,
            project_id=project_id
        )
        
        # Create document record
        document = doc_repo.create({
            "project_id": project_id,
            "filename": file_request.filename,
            "s3_key": s3_key,
            "file_size": file_request.file_size,
            "file_type": file_request.file_type,
            "processing_status": ProcessingStatus.UPLOADING.value,
            "clerk_id": clerk_id
        })
        
        return {
            "message": "Upload URL generated successfully",
            "data": {
                "upload_url": presigned_url,
                "s3_key": s3_key,
                "document": document
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate presigned URL: {str(e)}"
        )


@router.post("/{project_id}/files/confirm")
async def confirm_file_upload(
    project_id: str,
    confirm_request: FileConfirmRequest,
    clerk_id: CurrentUser
):
    """Confirm file upload and start processing."""
    # Update document status
    result = supabase.table("project_documents").update({
        "processing_status": ProcessingStatus.QUEUED.value
    }).eq("s3_key", confirm_request.s3_key)\
      .eq("project_id", project_id)\
      .eq("clerk_id", clerk_id)\
      .execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    document = result.data[0]
    document_id = document["id"]
    
    # Start Celery task
    task = celery_app.send_task(
            "src.tasks.document_tasks.processing_document",
            args=[document_id]
        )
    print(f"🚀 Started Celery task: {task.id}")
    
    # Store task ID
    doc_repo.update_task_id(document_id, task.id)
    
    return {
        "message": "Upload confirmed, processing started",
        "data": document
    }


@router.post("/{project_id}/urls")
async def process_url(
    project_id: str,
    url_request: UrlRequest,
    clerk_id: CurrentUser
):
    """Add URL for processing."""
    # Normalize URL
    url = url_request.url
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    
    try:
        # Create document record
        document = doc_repo.create({
            "project_id": project_id,
            "filename": url,
            "s3_key": "",
            "file_size": 0,
            "file_type": "text/html",
            "processing_status": ProcessingStatus.QUEUED.value,
            "clerk_id": clerk_id,
            "source_type": SourceType.URL.value,
            "source_url": url
        })
        
        document_id = document["id"]
        
        # Start Celery task
        task = processing_document.delay(document_id)
        
        # Store task ID
        doc_repo.update_task_id(document_id, task.id)
        
        return {
            "message": "URL added and processing started",
            "data": document
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process URL: {str(e)}"
        )


@router.delete("/{project_id}/files/{file_id}")
async def delete_file(
    project_id: str,
    file_id: str,
    clerk_id: CurrentUser
):
    """Delete a file and its chunks."""
    # Verify ownership
    doc = doc_repo.get_by_id(file_id)
    
    if not doc or doc.get("project_id") != project_id or doc.get("clerk_id") != clerk_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    # Delete from S3 if applicable
    s3_key = doc.get("s3_key")
    if s3_key:
        s3_client = S3Service()
        s3_client.delete_file(s3_key)
    
    # Delete document (chunks deleted via CASCADE)
    deleted = doc_repo.delete(file_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )
    
    return {
        "message": "Document deleted successfully",
        "data": deleted
    }


@router.get("/{project_id}/files/{file_id}/chunks")
async def get_document_chunks(
    project_id: str,
    file_id: str,
    clerk_id: CurrentUser
):
    """Get all chunks for a document."""
    # Verify project access
    if not project_repo.exists(project_id, clerk_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    # Verify document exists
    doc = doc_repo.get_by_id(file_id)
    if not doc or doc.get("project_id") != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    chunks = chunk_repo.get_by_document(file_id)
    
    return {
        "message": "Document chunks retrieved successfully",
        "data": chunks
    }
