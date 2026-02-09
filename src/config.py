"""BIRS configuration. All paths and model names in one place."""

import os
from pathlib import Path

# Base paths (project root = parent of src)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("BIRS_DATA_DIR", str(PROJECT_ROOT / "data")))
DOCUMENTS_DIR = DATA_DIR / "documents"
# Single JSON file for all document data (clean + poison). This is the source of truth.
DOCUMENTS_JSON = DOCUMENTS_DIR / "documents.json"
CLEAN_DIR = DOCUMENTS_DIR / "clean"  # Empty (legacy); kept for backward compatibility
POISON_DIR = DOCUMENTS_DIR / "poison"  # Empty (legacy); kept for backward compatibility
CHROMA_DIR = Path(os.getenv("BIRS_CHROMA_DIR", str(DATA_DIR / "chroma_birs")))
RESULTS_DIR = PROJECT_ROOT / "results"

# ChromaDB collection names
COLLECTION_CLEAN = "birs_clean"  # 5 truthful docs only (baseline)
COLLECTION_POISONED = "birs_poisoned"  # 5 clean + 15 poison (attack simulation)

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Brand (real product for real-life clean data; use BIRS_BRAND_NAME to override)
BRAND_NAME = os.getenv("BIRS_BRAND_NAME", "Manus")

# RAG
RAG_TOP_K = 5
RAG_TEMPERATURE = 0.0

# Embedding model (local)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
