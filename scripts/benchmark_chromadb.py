#!/usr/bin/env python3
"""Benchmark basic ChromaDB operations.

Prints JSON to stdout.
"""

import json
import time
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from src.config import CHROMA_DIR


def main() -> None:
    chroma_dir = Path(CHROMA_DIR)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    start_load = time.time()
    vs = Chroma(persist_directory=str(chroma_dir), embedding_function=embeddings)
    end_load = time.time()

    start_search = time.time()
    _ = vs.similarity_search("Manus AI", k=3)
    end_search = time.time()

    results = {
        "chroma_dir_exists": chroma_dir.exists(),
        "load_ms": round((end_load - start_load) * 1000, 2),
        "search_ms": round((end_search - start_search) * 1000, 2),
    }

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
