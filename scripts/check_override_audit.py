#!/usr/bin/env python3
"""C17: Validate that the audit agent denies modifying/deleting audit logs.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    policy_file = BASE_DIR / "agents" / "audit" / "policy.yaml"
    if not policy_file.exists():
        print(f"FAILED — {policy_file} not found", file=sys.stderr)
        return 1

    with open(policy_file) as f:
        policy = yaml.safe_load(f)

    errors: list[str] = []

    deny_actions = policy.get("deny", {}).get("actions", [])
    if "modify_audit_log" not in deny_actions:
        errors.append("audit policy missing deny action: modify_audit_log")
    if "delete_audit_log" not in deny_actions:
        errors.append("audit policy missing deny action: delete_audit_log")

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print("PASSED — check_override_audit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
