import os
from typing import List, Dict, Any, Optional

from langchain_core.messages import HumanMessage

from src.models.enums import SourceType, ProcessingStatus
from src.services.document.parser import DocumentParser
from src.services.document.chunker import DocumentChunker
from src.services.llm.embeddings import embedding_service
from src.services.llm.chat import chat_service


class DocumentProcessor:
    """Orchestrates document processing pipeline."""
    
    def __init__(self):
        self.parser = DocumentParser()
        self.chunker = DocumentChunker()
    
    def parse_document(
        self,
        file_path: str,
        file_type: str,
        source_type: SourceType = SourceType.FILE
    ) -> tuple[List[Any], Dict[str, int]]:
        """
        Parse document and return elements with analysis.
        
        Returns:
            Tuple of (elements, element_summary)
        """
        elements = self.parser.parse(file_path, file_type, source_type)
        summary = self.parser.analyze_elements(elements)
        
        return elements, summary
    
    def chunk_elements(
        self,
        elements: List[Any]
    ) -> tuple[List[Any], Dict[str, Any]]:
        """
        Chunk elements and return with metrics.
        
        Returns:
            Tuple of (chunks, chunking_metrics)
        """
        return self.chunker.chunk(elements)
    
    def process_chunks(
        self,
        chunks: List[Any],
        document_id: str,
        source_type: SourceType = SourceType.FILE,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Process all chunks with AI summaries.
        
        Args:
            chunks: List of document chunks
            document_id: Document ID for tracking
            source_type: Source type (file or URL)
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of processed chunk dictionaries
        """
        processed_chunks = []
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks):
            current_chunk = i + 1
            print(f"   Processing chunk {current_chunk}/{total_chunks}")
            
            if progress_callback:
                progress_callback(current_chunk, total_chunks)
            
            # Separate content types
            content_data = self.chunker.separate_content_types(chunk, source_type)
            
            # Create AI-enhanced summary if chunk has tables/images
            if content_data["tables"] or content_data["images"]:
                try:
                    enhanced_content = self._create_ai_summary(
                        content_data["text"],
                        content_data["tables"],
                        content_data["images"]
                    )
                except Exception as e:
                    print(f"     ❌ AI summary failed: {e}")
                    enhanced_content = content_data["text"]
            else:
                enhanced_content = content_data["text"]
            
            # Build original_content structure
            original_content = {"text": content_data["text"]}
            if content_data["tables"]:
                original_content["tables"] = content_data["tables"]
            if content_data["images"]:
                original_content["images"] = content_data["images"]
            
            # Create processed chunk
            processed_chunk = {
                "content": enhanced_content,
                "original_content": original_content,
                "type": content_data["types"],
                "page_number": self.chunker.get_page_number(chunk, i),
                "char_count": len(enhanced_content)
            }
            
            processed_chunks.append(processed_chunk)
        
        return processed_chunks
    
    def generate_embeddings(
        self,
        processed_chunks: List[Dict[str, Any]],
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for processed chunks.
        
        Returns:
            Processed chunks with embeddings added
        """
        texts = [chunk["content"] for chunk in processed_chunks]
        embeddings = embedding_service.embed_batch(texts, batch_size)
        
        for chunk, embedding in zip(processed_chunks, embeddings):
            chunk["embedding"] = embedding
        
        return processed_chunks
    
    def _create_ai_summary(
        self,
        text: str,
        tables_html: List[str],
        images_base64: List[str]
    ) -> str:
        """Create AI-enhanced summary for mixed content."""
        prompt_text = f"""Create a searchable index for this document content.

CONTENT:
{text}

"""
        
        if tables_html:
            prompt_text += "TABLES:\n"
            for i, table in enumerate(tables_html):
                prompt_text += f"Table {i+1}:\n{table}\n\n"
        
        prompt_text += """
Generate a structured search index (aim for 250-400 words):

QUESTIONS: List 5-7 key questions this content answers

KEYWORDS: Include:
- Specific data (numbers, dates, percentages)
- Core concepts and themes
- Technical terms and alternatives

VISUALS (if images present):
- Chart/graph types and insights
- Key patterns visible

DATA RELATIONSHIPS (if tables present):
- Column headers and meanings
- Key metrics and patterns

SEARCH INDEX:"""
        
        # Build multi-modal message
        message_content = [{"type": "text", "text": prompt_text}]
        
        for img_base64 in images_base64:
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
            })
        
        message = HumanMessage(content=message_content)
        
        from src.services.llm.providers.openrouter import OpenRouterProvider
        provider = OpenRouterProvider()
        return provider.invoke_with_images([message])
