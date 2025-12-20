import os
from typing import Dict, Any, cast

from scrapingbee import ScrapingBeeClient

from src.tasks.celery_app import celery_app
from src.config import settings
from src.models.enums import ProcessingStatus, SourceType
from src.services.database.supabase import supabase
from src.services.database.repositories.document_repo import (
    DocumentRepository,
    DocumentChunkRepository,
)
from src.services.storage.s3 import S3Service
from src.services.document.processor import DocumentProcessor


# Initialize ScrapingBee client
scrapingbee_client = ScrapingBeeClient(api_key=settings.SCRAPINGBEE_API_KEY)


@celery_app.task(bind=True, max_retries=3)
def processing_document(self, document_id: str) -> Dict[str, Any]:
    """
    Celery task for processing uploaded documents.
    
    Pipeline:
    1. Download from S3 / Crawl URL
    2. Partition document into elements
    3. Chunk elements
    4. Summarize chunks with AI
    5. Generate embeddings
    6. Store chunks in database
    
    Args:
        document_id: ID of the document to process
        
    Returns:
        Dict with status and document_id
    """
    doc_repo = DocumentRepository()
    chunk_repo = DocumentChunkRepository()
    processor = DocumentProcessor()
    temp_file = None
    
    try:
        # Get document record
        doc_result = supabase.table("project_documents")\
            .select("*")\
            .eq("id", document_id)\
            .execute()
        
        if not doc_result.data:
            raise Exception(f"Document not found: {document_id}")
        
        document = doc_result.data[0]
        source_type = SourceType(document.get("source_type", "file")) # type: ignore
        
        # Step 1: Download and partition
        print(f"📥 Step 1: Downloading and partitioning document {document_id}")
        doc_repo.update_status(document_id, ProcessingStatus.PARTITIONING.value) 
        print(f"Step -1.1 : {ProcessingStatus.PARTITIONING.value}")
        
        
        temp_file = _download_document(document_id, document, source_type) # type: ignore
        file_type = _get_file_type(document, source_type) # type: ignore
        
        elements, element_summary = processor.parse_document(
            temp_file, file_type, source_type
        )
        
        doc_repo.update_status(
            document_id,
            ProcessingStatus.CHUNKING.value,
            {"partitioning": {"elements_found": element_summary}}
        )
        print(f"Step -1.2 : {ProcessingStatus.CHUNKING.value}")
        
        # Step 2: Chunk elements
        print(f"✂️ Step 2: Chunking {len(elements)} elements")
        chunks, chunking_metrics = processor.chunk_elements(elements)
        
        doc_repo.update_status(
            document_id,
            ProcessingStatus.SUMMARIZING.value,
            {"chunking": chunking_metrics}
        )
        print(f"Step -2 : {ProcessingStatus.SUMMARIZING.value}")
        
        # Step 3: Process chunks with AI summaries
        print(f"🧠 Step 3: Processing {len(chunks)} chunks with AI")
        
        def progress_callback(current, total):
            doc_repo.update_status(
                document_id,
                ProcessingStatus.SUMMARIZING.value,
                {"summarizing": {"current_chunk": current, "total_chunks": total}}
            )
        
        processed_chunks = processor.process_chunks(
            chunks,
            document_id,
            source_type,
            progress_callback
        )
        
        # Step 4: Generate embeddings
        print(f"🔢 Step 4: Generating embeddings")
        doc_repo.update_status(document_id, ProcessingStatus.VECTORIZATION.value)
        print(f"Step -4 : {ProcessingStatus.VECTORIZATION.value}")
        
        processed_chunks = processor.generate_embeddings(processed_chunks)
        
        # Step 5: Store chunks in database
        print(f"💾 Step 5: Storing {len(processed_chunks)} chunks")
        
        for i, chunk_data in enumerate(processed_chunks):
            chunk_data["document_id"] = document_id
            chunk_data["chunk_index"] = i
            chunk_repo.insert_chunk(chunk_data)
        
        # Mark as completed
        doc_repo.update_status(document_id, ProcessingStatus.COMPLETED.value)
        print(f"Step -5 : {ProcessingStatus.COMPLETED.value}")
        print(f"✅ Celery task completed for document: {document_id}")
        
        return {
            "status": "success",
            "document_id": document_id,
            "chunks_created": len(processed_chunks)
        }
        
    except Exception as e:
        print(f"❌ Error processing document {document_id}: {str(e)}")
        doc_repo.update_status(
            document_id,
            ProcessingStatus.FAILED.value,
            {"error": str(e)}
        )
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        
    finally:
        # Cleanup temp file
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"🧹 Cleaned up temp file: {temp_file}")


def _download_document(
    document_id: str,
    document: Dict[str, Any],
    source_type: SourceType
) -> str:
    """Download document from S3 or crawl URL."""
    if source_type == SourceType.URL:
        url = document["source_url"]
        response = scrapingbee_client.get(url)
        
        temp_file = f"/tmp/{document_id}.html"
        with open(temp_file, "wb") as f:
            f.write(response.content)
        
        return temp_file
    else:
        s3_key = document.get("s3_key")
        if not s3_key:
            raise ValueError("Missing 's3_key' for S3 document download")
        
        filename = document.get("filename", "")
        file_type = filename.split(".")[-1].lower()
        
        s3_client = S3Service()
        return s3_client.download_file_to_temp(
            document_id=document_id,
            file_key=s3_key,
            file_type=file_type
        )


def _get_file_type(document: Dict[str, Any], source_type: SourceType) -> str:
    """Get file type from document."""
    if source_type == SourceType.URL:
        return "html"
    
    filename = document.get("filename", "")
    return filename.split(".")[-1].lower()
