#!/usr/bin/env python3
"""Run the extended suite and emit a concise results summary JSON to stdout.

This is used by the nightly GitHub Actions workflow.
"""

import json

from src.run_suite import run_suite


def main() -> None:
    results_path = run_suite(
        extended_tests=True,
        run_aeo_audit=True,
        run_deepeval=False,  # Don't require API key for nightly
    )

    with open(results_path) as f:
        data = json.load(f)

    test_results = {}
    for key, value in data.items():
        if key.startswith("birs_") and isinstance(value, dict):
            test_results[key] = {
                "pass": bool(value.get("pass", False)),
                "score": value.get("score", 0),
            }

    passing_tests = sum(1 for t in test_results.values() if t["pass"])
    avg_score = (
        sum(t["score"] for t in test_results.values()) / len(test_results)
        if test_results
        else 0
    )

    summary = {
        "results_path": results_path,
        "total_tests": len(test_results),
        "baseline_answer_length": len(data.get("baseline_answer", "")),
        "contexts_count": len(data.get("contexts", [])),
        "extended_tests_completed": True,
        "passing_tests": passing_tests,
        "avg_score": avg_score,
        "test_results": test_results,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
