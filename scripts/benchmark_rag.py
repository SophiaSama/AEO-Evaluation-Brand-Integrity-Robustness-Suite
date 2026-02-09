#!/usr/bin/env python3
"""Benchmark baseline RAG queries and write results JSON.

Reads NUM_QUERIES from environment (default 10).
Writes JSON summary to stdout.
"""

import json
import os
import time

from src.baseline import get_baseline_response


def main() -> None:
    num_queries = int(os.environ.get("NUM_QUERIES", "10"))
    results = []

    for i in range(num_queries):
        start = time.time()
        answer, contexts = get_baseline_response()
        end = time.time()

        results.append(
            {
                "query_num": i + 1,
                "latency_ms": round((end - start) * 1000, 2),
                "answer_length": len(answer),
                "contexts_retrieved": len(contexts),
            }
        )

    latencies = [r["latency_ms"] for r in results]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    summary = {
        "num_queries": num_queries,
        "avg_latency_ms": round(avg_latency, 2),
        "min_latency_ms": min(latencies) if latencies else 0,
        "max_latency_ms": max(latencies) if latencies else 0,
        "p95_latency_ms": (
            sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
        ),
        "queries": results,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
