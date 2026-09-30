#!/usr/bin/env python3
"""C15: Validate that the orchestrator has budget ceilings defined.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    policy_file = BASE_DIR / "agents" / "orchestrator" / "policy.yaml"
    if not policy_file.exists():
        print(f"FAILED — {policy_file} not found", file=sys.stderr)
        return 1

    with open(policy_file) as f:
        policy = yaml.safe_load(f)

    errors: list[str] = []

    budget = policy.get("budget")
    if not budget:
        errors.append("orchestrator policy missing budget section")
    else:
        if not budget.get("max_tokens_per_request", 0) > 0:
            errors.append("orchestrator budget max_tokens_per_request must be > 0")
        if not budget.get("max_tokens_per_day", 0) > 0:
            errors.append("orchestrator budget max_tokens_per_day must be > 0")
        if not budget.get("max_cost_per_day_usd", 0) > 0:
            errors.append("orchestrator budget max_cost_per_day_usd must be > 0")

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print("PASSED — check_budget")
    return 0


if __name__ == "__main__":
    sys.exit(main())
