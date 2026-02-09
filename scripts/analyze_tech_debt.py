#!/usr/bin/env python3
"""Analyze technical debt indicators in Python files."""

import json
import re
from pathlib import Path


def analyze_file(file_path):
    """Analyze a Python file for technical debt indicators."""
    content = Path(file_path).read_text()

    indicators = {
        "todos": len(re.findall(r"#\s*TODO", content, re.IGNORECASE)),
        "fixmes": len(re.findall(r"#\s*FIXME", content, re.IGNORECASE)),
        "hacks": len(re.findall(r"#\s*HACK", content, re.IGNORECASE)),
        "warnings": len(re.findall(r"#\s*WARNING", content, re.IGNORECASE)),
        "deprecated": len(
            re.findall(r"@deprecated|#\s*DEPRECATED", content, re.IGNORECASE)
        ),
        "long_functions": len(
            re.findall(r"def\s+\w+\([^)]*\):[^\n]*\n(    .*\n){30,}", content)
        ),
        "long_lines": len([line for line in content.split("\n") if len(line) > 120]),
    }

    return indicators


# Analyze all Python files
all_indicators = {}
totals = {
    "todos": 0,
    "fixmes": 0,
    "hacks": 0,
    "warnings": 0,
    "deprecated": 0,
    "long_functions": 0,
    "long_lines": 0,
}

for py_file in Path("src/").glob("*.py"):
    if py_file.name.startswith("_"):
        continue

    indicators = analyze_file(py_file)
    all_indicators[str(py_file)] = indicators

    for key in totals:
        totals[key] += indicators[key]

# Calculate debt score (higher = more debt)
debt_score = (
    totals["todos"] * 1
    + totals["fixmes"] * 2
    + totals["hacks"] * 3
    + totals["warnings"] * 2
    + totals["deprecated"] * 3
    + totals["long_functions"] * 5
    + totals["long_lines"] * 0.1
)

result = {"totals": totals, "debt_score": round(debt_score, 2), "files": all_indicators}

with open("tech_debt.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
