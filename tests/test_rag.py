"""Tests for RAG module (structure and config; full RAG requires Ollama + Chroma)."""

import pytest

from src.config import CHROMA_DIR, COLLECTION_CLEAN
from src.rag import get_retriever


def test_get_retriever_when_chroma_exists():
    """If ChromaDB was populated by ingest, retriever should be built."""
    if not CHROMA_DIR.exists():
        pytest.skip("Chroma not populated; run scripts/ingest_documents.py first")
    r = get_retriever(COLLECTION_CLEAN)
    assert r is not None
