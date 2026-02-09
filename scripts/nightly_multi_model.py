#!/usr/bin/env python3
"""Run a lightweight multi-model nightly check.

This script is intended for GitHub Actions. It writes JSON results to stdout.
"""

import json

from src.run_suite import run_suite


def main() -> None:
    # The workflow controls which models are available/pulled.
    results_path = run_suite(
        extended_tests=False,
        run_aeo_audit=False,
        run_deepeval=False,
        multi_model=True,
    )

    with open(results_path) as f:
        data = json.load(f)

    summary = {
        "results_path": results_path,
        "models": data.get("models", []),
        "status": data.get("status", "unknown"),
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
