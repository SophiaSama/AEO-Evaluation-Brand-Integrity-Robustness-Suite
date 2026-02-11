"""
Ingest documents from documents.json into ChromaDB.
Creates two collections:
- birs_clean: 5 truthful docs only (baseline)
- birs_poisoned: 5 clean + 15 poison docs (attack simulation)

Run from project root: python scripts/ingest_documents.py
"""

import json

from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

from src.config import (
    CHROMA_DIR,
    COLLECTION_CLEAN,
    COLLECTION_POISONED,
    DOCUMENTS_JSON,
    EMBEDDING_MODEL,
)


def load_documents() -> dict:
    """Load documents from documents.json."""
    if not DOCUMENTS_JSON.exists():
        raise FileNotFoundError(
            f"documents.json not found at {DOCUMENTS_JSON}. "
            "Create it first or use scripts/build_documents_json.py to generate from .txt files."
        )

    with open(DOCUMENTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "clean" not in data or "poison" not in data:
        raise ValueError("documents.json must have 'clean' and 'poison' keys")

    return data


def ingest_collection(client, collection_name: str, documents: list[dict], embedder):
    """
    Ingest documents into a ChromaDB collection.
    Each document should have: id, source, source_name, content
    """
    # Delete collection if it exists (fresh ingest)
    try:
        client.delete_collection(collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except Exception:
        pass

    # Create collection
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": f"BIRS collection: {collection_name}"},
    )

    if not documents:
        print(f"No documents to ingest for {collection_name}")
        return

    # Prepare data
    ids = [doc["id"] for doc in documents]
    contents = [doc["content"] for doc in documents]
    metadatas = [
        {
            "source": doc.get("source", ""),
            "source_name": doc.get("source_name", "unknown"),
        }
        for doc in documents
    ]

    # Generate embeddings
    print(f"Generating embeddings for {len(documents)} documents...")
    embeddings = embedder.encode(contents, show_progress_bar=True).tolist()

    # Add to collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=contents,
        metadatas=metadatas,
    )

    print(f"✓ Ingested {len(documents)} documents into {collection_name}")


def main():
    """Main ingestion workflow."""
    print("=" * 60)
    print("BIRS Document Ingestion")
    print("=" * 60)

    # Load documents
    print(f"\nLoading documents from {DOCUMENTS_JSON}...")
    data = load_documents()
    clean_docs = data["clean"]
    poison_docs = data["poison"]

    print(f"Found {len(clean_docs)} clean documents")
    print(f"Found {len(poison_docs)} poison documents")

    # Initialize ChromaDB
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = PersistentClient(path=str(CHROMA_DIR))

    # Load embedding model
    print(f"\nLoading embedding model: {EMBEDDING_MODEL}")
    print("(First run will download the model, ~80MB)")
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    # Ingest clean collection (baseline)
    print(f"\n1. Ingesting CLEAN collection ({COLLECTION_CLEAN})...")
    ingest_collection(client, COLLECTION_CLEAN, clean_docs, embedder)

    # Ingest poisoned collection (clean + poison)
    print(f"\n2. Ingesting POISONED collection ({COLLECTION_POISONED})...")
    combined_docs = clean_docs + poison_docs
    ingest_collection(client, COLLECTION_POISONED, combined_docs, embedder)

    print("\n" + "=" * 60)
    print("✓ Ingestion complete!")
    print("=" * 60)
    print(f"\nChromaDB location: {CHROMA_DIR}")
    print("Collections created:")
    print(f"  - {COLLECTION_CLEAN}: {len(clean_docs)} documents (clean only)")
    print(f"  - {COLLECTION_POISONED}: {len(combined_docs)} documents (clean + poison)")
    print("\nNext steps:")
    print("  - Run baseline: python -m src.baseline")
    print("  - Run full suite: python -m src.run_suite")


if __name__ == "__main__":
    main()
