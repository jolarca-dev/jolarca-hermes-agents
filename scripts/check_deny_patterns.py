#!/usr/bin/env python3
"""Scan for forbidden mission-platform references (ADR-0004 R4).

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.

Fails when any file in the repository contains references to:
  * journeyoflife-org (mission GitHub org)
  * jol-* (mission repo prefix)
  * /opt/jol/ (mission local tree)

Exceptions:
  * This script itself (it contains the patterns as strings)
  * .git/ directory
  * .venv/ directory
  * Policy files that DENY these patterns (they contain the strings
    as deny-list entries, not as references)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Patterns that indicate a mission-platform reference.
# These are checked against file content line-by-line.
FORBIDDEN_PATTERNS = [
    re.compile(r"journeyoflife-org"),
    re.compile(r"\bjol-(?!arca)"),  # jol-* but NOT jolarca*
    re.compile(r"/opt/jol/"),
    re.compile(r"/opt/jol-m/"),
]

# Files/directories to skip
SKIP_DIRS = {".git", ".venv", ".idea", "__pycache__", "node_modules", "tests"}
SKIP_FILES = {"check_deny_patterns.py"}  # This script itself

# File patterns to skip (they legitimately mention forbidden patterns as examples)
SKIP_SUFFIXES = {".py"}  # Python files (tests, scripts) often contain patterns as strings


def scan_file(filepath: Path) -> list[str]:
    """Scan a single file for forbidden patterns. Returns list of violations."""
    violations: list[str] = []

    # Skip policy files that contain deny-list entries
    # (they legitimately contain the patterns as strings to deny)
    if filepath.name in ("policy.yaml", "agent.yaml"):
        return violations

    # Skip Python files (tests, scripts contain patterns as strings)
    if filepath.suffix in SKIP_SUFFIXES:
        return violations

    # Skip agent prompt files (they mention patterns as things to avoid)
    if "prompts" in filepath.parts:
        return violations

    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return violations

    for line_num, line in enumerate(content.splitlines(), 1):
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(line):
                rel_path = filepath.relative_to(BASE_DIR)
                violations.append(f"{rel_path}:{line_num}: forbidden pattern '{pattern.pattern}' found")

    return violations


def main() -> int:
    all_violations: list[str] = []
    file_count = 0

    for filepath in sorted(BASE_DIR.rglob("*")):
        if not filepath.is_file():
            continue

        # Skip excluded directories
        parts = filepath.relative_to(BASE_DIR).parts
        if any(part in SKIP_DIRS for part in parts):
            continue

        # Skip excluded files
        if filepath.name in SKIP_FILES:
            continue

        # Skip binary files
        if filepath.suffix in (".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf"):
            continue

        file_count += 1
        violations = scan_file(filepath)
        all_violations.extend(violations)

    if all_violations:
        print(f"FAILED — {len(all_violations)} violation(s) in {file_count} file(s):\n")
        for v in all_violations:
            print(f"  x {v}")
        print("\nADR-0004 R4: marketplace repos must not reference mission-platform resources.")
        return 1

    print(f"PASSED — {file_count} file(s) scanned, no violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
