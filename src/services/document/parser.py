import os
from typing import List, Dict, Any, Optional

from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.html import partition_html
from unstructured.partition.pptx import partition_pptx
from unstructured.partition.text import partition_text
from unstructured.partition.md import partition_md

from src.models.enums import FileType, SourceType


class DocumentParser:
    """Service for parsing documents into elements."""
    
    PARTITION_FUNCTIONS = {
        FileType.PDF: partition_pdf,
        FileType.DOCX: partition_docx,
        FileType.PPTX: partition_pptx,
        FileType.TXT: partition_text,
        FileType.MD: partition_md,
        FileType.HTML: partition_html,
    }
    
    def parse(
        self,
        file_path: str,
        file_type: str,
        source_type: SourceType = SourceType.FILE
    ) -> List[Any]:
        """
        Parse a document into unstructured elements.
        
        Args:
            file_path: Path to the document
            file_type: File extension/type
            source_type: Whether it's a file or URL
            
        Returns:
            List of unstructured elements
        """
        if source_type == SourceType.URL:
            return partition_html(filename=file_path)
        
        file_type_enum = self._get_file_type_enum(file_type)
        
        if file_type_enum == FileType.PDF:
            return partition_pdf(
                filename=file_path,
                strategy="hi_res",
                infer_table_structure=True,
                extract_image_block_types=["Image"],
                extract_image_block_to_payload=True
            )
        elif file_type_enum == FileType.DOCX:
            return partition_docx(
                filename=file_path,
                strategy="hi_res",
                infer_table_structure=True
            )
        elif file_type_enum == FileType.PPTX:
            return partition_pptx(
                filename=file_path,
                strategy="hi_res",
                infer_table_structure=True
            )
        elif file_type_enum == FileType.TXT:
            return partition_text(filename=file_path)
        elif file_type_enum == FileType.MD:
            return partition_md(filename=file_path)
        elif file_type_enum == FileType.HTML:
            return partition_html(filename=file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _get_file_type_enum(self, file_type: str) -> FileType:
        """Convert string file type to enum."""
        file_type_lower = file_type.lower().strip(".")
        
        try:
            return FileType(file_type_lower)
        except ValueError:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    @staticmethod
    def analyze_elements(elements: List[Any]) -> Dict[str, int]:
        """
        Analyze parsed elements and count by type.
        
        Args:
            elements: List of unstructured elements
            
        Returns:
            Dictionary with counts by element type
        """
        counts = {
            "text": 0,
            "table": 0,
            "image": 0,
            "title": 0,
            "other": 0
        }
        
        for element in elements:
            element_name = type(element).__name__
            
            if element_name == "Table":
                counts["table"] += 1
            elif element_name == "Image":
                counts["image"] += 1
            elif element_name in ["NarrativeText", "Text", "ListItem", "FigureCaption"]:
                counts["text"] += 1
            elif element_name in ["Title", "Header"]:
                counts["title"] += 1
            else:
                counts["other"] += 1
        
        return counts
