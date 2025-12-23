"""
RAGAS Evaluation Script
"""

import json
from pathlib import Path
from dotenv import load_dotenv
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
load_dotenv(project_root / ".env")

from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.metrics import faithfulness, answer_relevancy, context_precision

from src.config import settings


def load_dataset(path: Path) -> EvaluationDataset:
    """Load dataset from JSON file."""
    with open(path, 'r') as f:
        data = json.load(f)
    
    samples = [
        SingleTurnSample(
            user_input=item["question"],
            retrieved_contexts=item["contexts"],
            response=item["answer"],
            #reference=item.get("ground_truth")
        )
        for item in data
    ]
    return EvaluationDataset(samples=samples)  


def get_ragas_config():
    """Configure LLM and embeddings for RAGAS."""
    llm = LangchainLLMWrapper(
        ChatOpenAI(
            model="openai/gpt-4o-mini",
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY
        )
    )
    
    embeddings = LangchainEmbeddingsWrapper(
        OpenAIEmbeddings(
            model=settings.DEFAULT_EMBEDDING_MODEL,
            dimensions=settings.EMBEDDING_DIMENSIONS,
            openai_api_base=settings.OPENROUTER_BASE_URL,
            openai_api_key=settings.OPENROUTER_API_KEY
        )
    )
    
    return llm, embeddings


def run_evaluation(dataset_path: Path):
    """Run RAGAS evaluation on dataset."""
    
    print(f"Loading dataset from {dataset_path}")
    dataset = load_dataset(dataset_path)
    
    print("Configuring RAGAS...")
    llm, embeddings = get_ragas_config()
    
    print(f"Evaluating {len(dataset.samples)} samples...")
    results = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=llm,
        embeddings=embeddings
    )
    
    print("\n" + "="*50)
    print("EVALUATION RESULTS")
    print("="*50)
    print(results)
    
    # Save detailed results
    df = results.to_pandas()
    output_path = dataset_path.parent / "evaluation_results.csv"
    df.to_csv(output_path, index=False)
    print(f"\n✅ Detailed results saved to {output_path}")
    
    return results


if __name__ == "__main__":
    dataset_path = Path(__file__).parent / "datasets" / "ragas_evaluation_dataset-1.json"
    run_evaluation(dataset_path)
