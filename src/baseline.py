"""
Phase 1: Baseline — "Clean" sandbox only.
Run RAG with only the 5 truthful docs (birs_clean) and store response for later comparison.
"""
from src.config import BRAND_NAME
from src.rag import query_rag_with_context


def get_baseline_response(
    question: str | None = None,
    brand: str | None = None,
) -> tuple[str, list[str]]:
    """
    Query the RAG sandbox with clean-only data (birs_clean).
    Returns (answer, list of retrieved context strings).
    """
    brand = brand or BRAND_NAME
    q = question or f"What is {brand} known for?"
    answer, contexts = query_rag_with_context(q, use_clean_only=True)
    return answer, contexts


def get_baseline_queries(brand: str | None = None) -> list[str]:
    """Standard queries used for baseline and test cases."""
    brand = brand or BRAND_NAME
    return [
        f"What is {brand} known for?",
        f"Is {brand} safe to use for families in Singapore?",
    ]
