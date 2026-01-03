from fastapi import APIRouter, HTTPException, status
from src.api.deps import CurrentUser
from src.services.database.repositories.chunk_repo import chunk_repo
from src.schemas.chunks import ChunkResponse

router = APIRouter()


@router.get("/{chunk_id}", response_model=ChunkResponse)
async def get_chunk_details(
    chunk_id: str,
    clerk_id: CurrentUser
):
    """
    Get chunk details by ID.
    
    Returns chunk content, metadata, and associated document filename.
    Used for citation popups in the chat interface.
    """
    try:
        # Get chunk with document info (includes ownership check)
        chunk = chunk_repo.get_chunk_with_document(chunk_id, clerk_id)
        
        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chunk not found or access denied"
            )
        
        return ChunkResponse(
            id=chunk["id"],
            document_id=chunk["document_id"],
            content=chunk["content"],
            chunk_index=chunk["chunk_index"],
            page_number=chunk["page_number"],
            char_count=chunk["char_count"],
            type=chunk["type"],
            original_content=chunk.get("original_content"),
            filename=chunk["project_documents"]["filename"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching chunk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )