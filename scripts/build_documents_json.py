"""
Build or update data/documents/documents.json from clean/*.txt and poison/*.txt.
Run from project root: python scripts/build_documents_json.py
If documents.json already exists, this overwrites it from the current .txt files.
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CLEAN_DIR, DOCUMENTS_DIR, DOCUMENTS_JSON, POISON_DIR


def _source_name_from_stem(stem: str) -> str:
    stem_lower = stem.lower()
    if "reddit" in stem_lower or "forum" in stem_lower:
        return "reddit"
    return "press_release"


def build_from_dirs() -> dict:
    """Build { clean: [...], poison: [...] } from CLEAN_DIR and POISON_DIR."""
    clean = []
    for f in sorted(CLEAN_DIR.glob("*.txt")):
        clean.append({
            "id": f.stem,
            "source": f.name,
            "source_name": "official",
            "content": f.read_text(encoding="utf-8").strip(),
        })

    poison = []
    for f in sorted(POISON_DIR.glob("*.txt")):
        poison.append({
            "id": f.stem,
            "source": f.name,
            "source_name": _source_name_from_stem(f.stem),
            "content": f.read_text(encoding="utf-8").strip(),
        })

    return {"clean": clean, "poison": poison}


def main():
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    data = build_from_dirs()
    DOCUMENTS_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(data['clean'])} clean + {len(data['poison'])} poison entries to {DOCUMENTS_JSON}")


if __name__ == "__main__":
    main()
