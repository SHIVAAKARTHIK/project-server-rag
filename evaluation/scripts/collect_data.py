"""
RAGAS Data Collection Script
Runs test questions through your RAG system and collects evaluation data.
"""

import json
from pathlib import Path
import sys
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load .env BEFORE importing anything that uses settings
env_path = project_root / ".env"
load_dotenv(env_path)

from src.rag.pipeline import RAGPipeline
from src.services.database.repositories.project_repo import ProjectSettingsRepository
from src.services.database.repositories.document_repo import DocumentRepository
from src.rag.context_builder import build_context

# Configuration
PROJECT_ID = "02d8c51f-a3a2-4533-9ae1-8714bbedeeca"

TEST_QUESTIONS = [
    "What is autoimmune disorders an type of autoimmune disorders?",
    "How Genetics invoved in autoimmune disorders?"
]


def collect_rag_data(project_id: str, questions: list) -> list:
    """Run questions through RAG pipeline and collect data."""
    dataset = []
    
    for question in questions:
        print(f"Processing: {question}")
        settings_repo = ProjectSettingsRepository()
        doc_repo = DocumentRepository()
        document_ids = doc_repo.get_document_ids(project_id)
        print(settings_repo)
        settings = settings_repo.get_by_project_id(project_id)
        rag = RAGPipeline()
        result = rag.process(
            query=question,
            document_ids=document_ids,
            settings=settings  # type: ignore
        )
    
        texts, images, tables, citations = build_context(result['chunks'])
        
        # Prepare contexts for RAGAS
        contexts = texts + [f"[TABLE]\n{table}" for table in tables]
        
                
        dataset.append({
            "question": question,
            "contexts": contexts or ["No context found"],
            "answer": result['answer']
        })
        
        
        
    return dataset


if __name__ == "__main__":
    # Collect and save data
    dataset = collect_rag_data(PROJECT_ID, TEST_QUESTIONS)
    
    output_path = Path(__file__).parent / "datasets" / "ragas_evaluation_dataset-1.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(dataset)} questions to {output_path}")