#!/usr/bin/env python3
"""
Script: playbook_structure_linter.py
Purpose: Enforce 7-task Trinity workflow sequence (P2 Discipline)
Guardian: Carter (Guardian)
Maturity: v2.0.0

REQUIRED_TASKS = [
    "GATHER", "PROCESS", "APPLY", "VERIFY",
    "AUDIT", "REPORT", "FINALIZE"
]
"""

import sys
from pathlib import Path
from typing import Any

import yaml

# ============================================================================
# CONFIGURATION
# ============================================================================

REQUIRED_TASKS: list[str] = [
    "GATHER",
    "PROCESS",
    "APPLY",
    "VERIFY",
    "AUDIT",
    "REPORT",
    "FINALIZE",
]

# ============================================================================
# FUNCTIONS
# ============================================================================


def lint_playbook(file_path: str | Path) -> bool:
    print(f"Linting {file_path} for Trinity 7-task compliance...")

    with open(file_path) as f:
        try:
            content: Any = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(f"ERROR: YAML parse error in {file_path}: {exc}")
            return False

    if not isinstance(content, list):
        print(f"ERROR: Playbook {file_path} must be a list of plays.")
        return False

    all_valid = True
    for play in content:
        tasks: list[Any] = play.get("tasks", [])
        task_names: list[str] = [
            task.get("name", "").upper() for task in tasks if isinstance(task, dict)
        ]

        # Filter for canonical task names
        found_canonical: list[str] = [
            name for name in task_names if any(req in name for req in REQUIRED_TASKS)
        ]

        # Check order and completeness
        for i, req in enumerate(REQUIRED_TASKS):
            if i >= len(found_canonical):
                print(f"  [MISSING] Task {req}")
                all_valid = False
            elif req not in found_canonical[i]:
                print(f"  [MISORDERED] Expected {req}, found {found_canonical[i]}")
                all_valid = False
            else:
                print(f"  [OK] Task {req}")

    return all_valid


# ============================================================================
# EXECUTION (Carter Verification)
# ============================================================================


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: playbook_structure_linter.py <playbook1.yml> ...")
        sys.exit(1)

    overall_success: bool = True
    for playbook_path in sys.argv[1:]:
        if not lint_playbook(Path(playbook_path)):
            overall_success = False

    if not overall_success:
        print("\nRESULT: Trinity alignment FAILED. Check task order.")
        sys.exit(1)

    print("\nRESULT: Trinity alignment SUCCESS.")
    sys.exit(0)


if __name__ == "__main__":
    main()
