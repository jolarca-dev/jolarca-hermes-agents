#!/usr/bin/env python3
"""C2: Validate tenant-scoped access rules in the rag agent.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    policy_file = BASE_DIR / "agents" / "rag" / "policy.yaml"
    if not policy_file.exists():
        print(f"FAILED — {policy_file} not found", file=sys.stderr)
        return 1

    with open(policy_file) as f:
        policy = yaml.safe_load(f)

    errors: list[str] = []

    deny = policy.get("deny", {})
    deny_actions = deny.get("actions", [])
    if "cross_tenant_index_access" not in deny_actions:
        errors.append("rag policy missing deny action: cross_tenant_index_access")

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print("PASSED — check_tenant_isolation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
