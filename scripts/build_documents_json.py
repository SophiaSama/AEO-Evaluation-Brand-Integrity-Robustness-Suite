"""
[LEGACY SCRIPT - No longer needed in standard workflow]

Build or update data/documents/documents.json from clean/*.txt and poison/*.txt.

This script is kept for backward compatibility if you have existing .txt files
to convert to the JSON format. In the current workflow, documents.json is
manually edited or updated by the crawler.

Run from project root: python scripts/build_documents_json.py

Note: The clean/ and poison/ directories are now empty by default.
All document data should be managed through documents.json directly.
"""

import json
import sys
from pathlib import Path

# Add project root to path to allow importing from src
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (  # noqa: E402
    CLEAN_DIR,
    DOCUMENTS_DIR,
    DOCUMENTS_JSON,
    POISON_DIR,
)


def _source_name_from_stem(stem: str) -> str:
    stem_lower = stem.lower()
    if "reddit" in stem_lower or "forum" in stem_lower:
        return "reddit"
    return "press_release"


def build_from_dirs() -> dict:
    """Build { clean: [...], poison: [...] } from CLEAN_DIR and POISON_DIR."""
    clean = []
    for f in sorted(CLEAN_DIR.glob("*.txt")):
        clean.append(
            {
                "id": f.stem,
                "source": f.name,
                "source_name": "official",
                "content": f.read_text(encoding="utf-8").strip(),
            }
        )

    poison = []
    for f in sorted(POISON_DIR.glob("*.txt")):
        poison.append(
            {
                "id": f.stem,
                "source": f.name,
                "source_name": _source_name_from_stem(f.stem),
                "content": f.read_text(encoding="utf-8").strip(),
            }
        )

    return {"clean": clean, "poison": poison}


def main():
    print("=" * 70)
    print("WARNING: This is a LEGACY script.")
    print("The current workflow uses documents.json directly.")
    print("This script only needed if you have existing .txt files to convert.")
    print("=" * 70)
    print()

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    data = build_from_dirs()

    if not data["clean"] and not data["poison"]:
        print("ERROR: No .txt files found in clean/ or poison/ directories.")
        print("The current workflow expects documents.json to already exist.")
        print("If you need to add documents, edit documents.json directly.")
        return

    DOCUMENTS_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(
        f"Wrote {len(data['clean'])} clean + {len(data['poison'])} poison entries to {DOCUMENTS_JSON}"
    )
    print()
    print("Next step: Run 'python scripts/ingest_documents.py' to populate ChromaDB")


if __name__ == "__main__":
    main()
