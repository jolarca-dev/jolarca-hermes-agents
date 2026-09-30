#!/usr/bin/env python3
"""C12: Validate that the guardrails agent has injection defence rules.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    policy_file = BASE_DIR / "agents" / "guardrails" / "policy.yaml"
    if not policy_file.exists():
        print(f"FAILED — {policy_file} not found", file=sys.stderr)
        return 1

    with open(policy_file) as f:
        policy = yaml.safe_load(f)

    errors: list[str] = []

    # guardrails should have escalation patterns for injection detection
    escalation = policy.get("escalation", {})
    patterns = escalation.get("patterns", [])
    if not patterns:
        errors.append("guardrails policy missing escalation patterns for injection detection")

    # check that prompt_injection is among the escalation patterns
    if "prompt_injection" not in patterns:
        errors.append("guardrails escalation patterns missing: prompt_injection")

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print("PASSED — check_injection_defence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
