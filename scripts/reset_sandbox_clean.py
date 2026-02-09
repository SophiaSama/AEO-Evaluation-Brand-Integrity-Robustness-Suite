"""
Reset sandbox to "clean" only: re-ingest only the 5 clean documents into birs_clean.
Optionally wipe birs_poisoned so a fresh ingest_documents.py repopulates both.
Run from project root: python scripts/reset_sandbox_clean.py
"""

import shutil
import sys
from pathlib import Path

from src.config import CHROMA_DIR

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


if __name__ == "__main__":
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
        print(
            f"Removed {CHROMA_DIR}. Run scripts/ingest_documents.py to repopulate (clean + poisoned)."
        )
    else:
        print(f"{CHROMA_DIR} does not exist. Run scripts/ingest_documents.py first.")
