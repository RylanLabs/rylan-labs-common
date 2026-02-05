#!/usr/bin/env python3
"""
Script: track-endpoint-coverage.py
Purpose: Track and enforce API documentation coverage (P1 Discipline)
Guardian: Bauer (Auditor)
Maturity: v2.0.0
"""

import json
import sys
from pathlib import Path
from typing import Any

# ============================================================================
# CONFIGURATION
# ============================================================================

COVERAGE_FILE: Path = Path(".audit/api/coverage.json")
MIN_COVERAGE_PCT: int = 80

# ============================================================================
# FUNCTIONS
# ============================================================================


def load_coverage() -> dict[str, Any]:
    if not COVERAGE_FILE.exists():
        COVERAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        default_coverage: dict[str, Any] = {
            "total_endpoints": 0,
            "documented": 0,
            "coverage_pct": 0,
            "missing": [],
            "guardian_mapping": {},
        }
        return default_coverage

    with open(COVERAGE_FILE) as f:
        data: dict[str, Any] = json.load(f)
        return data


def validate_coverage(data: dict[str, Any]) -> bool:
    total: int = data.get("total_endpoints", 0)
    documented: int = data.get("documented", 0)

    if total == 0:
        print("Bauer: No endpoints identified. Discovery required.")
        return True

    pct: float = (documented / total) * 100
    data["coverage_pct"] = round(pct, 2)

    print(f"API Documentation Coverage: {data['coverage_pct']}%")

    if pct < MIN_COVERAGE_PCT:
        print(f"ERROR: Coverage below {MIN_COVERAGE_PCT}% threshold.")
        print(f"Missing endpoints: {', '.join(data.get('missing', []))}")
        return False

    return True


# ============================================================================
# EXECUTION (Bauer Verification)
# ============================================================================


def main() -> None:
    print("Starting API Coverage Audit (Maturity: v2.0.0)...")

    try:
        data: dict[str, Any] = load_coverage()
        if not validate_coverage(data):
            sys.exit(1)

        print("SUCCESS: API Coverage within threshold.")
        sys.exit(0)

    except Exception as e:
        print(f"ERROR: Audit failed - {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    main()
