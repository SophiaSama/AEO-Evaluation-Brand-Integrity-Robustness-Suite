#!/usr/bin/env python3
"""Benchmark embedding generation for different text sizes.

Prints JSON to stdout.
"""

import json
import time

from sentence_transformers import SentenceTransformer


def main() -> None:
    test_texts = {
        "short": "Manus AI agent",
        "medium": "Manus is an AI-powered autonomous agent that helps businesses automate complex workflows. "
        * 5,
        "long": "Manus is an AI-powered autonomous agent that helps businesses automate complex workflows. "
        * 50,
    }

    model = SentenceTransformer("all-MiniLM-L6-v2")
    results = {}

    for label, text in test_texts.items():
        start = time.time()
        vec = model.encode([text])
        end = time.time()
        results[label] = {
            "text_len": len(text),
            "embedding_dim": int(vec.shape[1]),
            "latency_ms": round((end - start) * 1000, 2),
        }

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
