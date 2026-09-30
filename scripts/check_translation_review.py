#!/usr/bin/env python3
"""C5: Validate that the translation agent flags sensitive terms.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    policy_file = BASE_DIR / "agents" / "translation" / "policy.yaml"
    if not policy_file.exists():
        print(f"FAILED — {policy_file} not found", file=sys.stderr)
        return 1

    with open(policy_file) as f:
        policy = yaml.safe_load(f)

    errors: list[str] = []

    # translation must have escalation rules for sensitive/doctrinal terms
    escalation = policy.get("escalation", {})
    if not escalation.get("patterns"):
        errors.append("translation policy missing escalation patterns")

    if not escalation.get("action"):
        errors.append("translation policy missing escalation action")

    # translation must deny translating without review for sensitive content
    deny_actions = policy.get("deny", {}).get("actions", [])
    if "publish_without_approval" not in deny_actions:
        errors.append("translation policy missing deny action: publish_without_approval")

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print("PASSED — check_translation_review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
