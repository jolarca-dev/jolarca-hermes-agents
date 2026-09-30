#!/usr/bin/env python3
"""C11: Validate that the consent agent denies PII in logs.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    policy_file = BASE_DIR / "agents" / "consent" / "policy.yaml"
    if not policy_file.exists():
        print(f"FAILED — {policy_file} not found", file=sys.stderr)
        return 1

    with open(policy_file) as f:
        policy = yaml.safe_load(f)

    errors: list[str] = []

    deny_actions = policy.get("deny", {}).get("actions", [])
    if "store_pii_in_logs" not in deny_actions:
        errors.append("consent policy missing deny action: store_pii_in_logs")
    if "cross_tenant_pii_access" not in deny_actions:
        errors.append("consent policy missing deny action: cross_tenant_pii_access")

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print("PASSED — check_pii_redaction")
    return 0


if __name__ == "__main__":
    sys.exit(main())
