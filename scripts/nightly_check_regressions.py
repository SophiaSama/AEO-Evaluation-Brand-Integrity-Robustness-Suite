#!/usr/bin/env python3
"""Check nightly results for regressions.

Reads `extended_results.json` and exits non-zero if minimum scores are not met.
"""

import json

MIN_ACCEPTABLE_SCORES = {
    "birs_01": 0.5,  # Grounding
    "birs_02": 0.5,  # Consistency
    "birs_03": 0.5,  # Robustness
    "birs_04": 0.6,  # Entity integrity
    "birs_05": 0.6,  # Citation veracity
    "birs_06": 0.6,  # Source attribution
}


def main() -> None:
    with open("extended_results.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    test_results = data.get("test_results", {})

    failures: list[str] = []
    for test_id, min_score in MIN_ACCEPTABLE_SCORES.items():
        result = test_results.get(test_id)
        if not result:
            failures.append(f"Missing result for {test_id}")
            continue

        score = float(result.get("score", 0))
        passed = bool(result.get("pass", False))

        if (not passed) or score < min_score:
            failures.append(
                f"{test_id} failed regression gate: pass={passed} score={score} < {min_score}"
            )

    if failures:
        print("❌ Regressions detected:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("✅ No regressions detected (all gates passed)")


if __name__ == "__main__":
    main()
