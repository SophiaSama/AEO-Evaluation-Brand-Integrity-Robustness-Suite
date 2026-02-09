#!/usr/bin/env python3
"""Generate coverage badge data from coverage.json"""

import json

with open("coverage.json") as f:
    data = json.load(f)
    coverage = data["totals"]["percent_covered"]

# Determine color
if coverage >= 80:
    color = "brightgreen"
elif coverage >= 60:
    color = "yellow"
elif coverage >= 40:
    color = "orange"
else:
    color = "red"

print(f"Coverage: {coverage:.1f}%")
print(f"Color: {color}")

# Create simple badge data
with open("coverage-badge.json", "w") as out:
    json.dump(
        {
            "schemaVersion": 1,
            "label": "coverage",
            "message": f"{coverage:.1f}%",
            "color": color,
        },
        out,
    )
