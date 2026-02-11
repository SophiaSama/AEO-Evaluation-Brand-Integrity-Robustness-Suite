"""Tests for RAG module (structure and config; full RAG requires Ollama + Chroma)."""

from src.config import COLLECTION_CLEAN
from src.rag import get_retriever


def test_get_retriever_when_chroma_exists(tmp_path, monkeypatch):
    """Ensure retriever can be built; if Chroma isn't populated, ingest first."""
    chroma_dir = tmp_path / "chroma_birs"
    data_dir = tmp_path / "data"

    monkeypatch.setenv("BIRS_CHROMA_DIR", str(chroma_dir))
    monkeypatch.setenv("BIRS_DATA_DIR", str(data_dir))

    if not chroma_dir.exists():
        # Lazy import after env vars so `src.config` reads the temp paths.
        from scripts.ingest_documents import main as ingest_main

        ingest_main()

    r = get_retriever(COLLECTION_CLEAN, chroma_dir=chroma_dir)
    assert r is not None
