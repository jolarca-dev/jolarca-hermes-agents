#!/usr/bin/env python3
"""C3: Validate that the editorial agent requires human approval.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    errors: list[str] = []

    # editorial agent must have human_approver gate
    agent_file = BASE_DIR / "agents" / "editorial" / "agent.yaml"
    if not agent_file.exists():
        print(f"FAILED — {agent_file} not found", file=sys.stderr)
        return 1

    with open(agent_file) as f:
        agent = yaml.safe_load(f)

    if agent.get("human_gate") != "human_approver":
        errors.append(f"editorial human_gate is '{agent.get('human_gate')}', expected 'human_approver'")

    # editorial policy must deny publishing without approval
    policy_file = BASE_DIR / "agents" / "editorial" / "policy.yaml"
    if not policy_file.exists():
        print(f"FAILED — {policy_file} not found", file=sys.stderr)
        return 1

    with open(policy_file) as f:
        policy = yaml.safe_load(f)

    deny_actions = policy.get("deny", {}).get("actions", [])
    if "approve_without_provenance" not in deny_actions:
        errors.append("editorial policy missing deny action: approve_without_provenance")

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print("PASSED — check_editorial_approval")
    return 0


if __name__ == "__main__":
    sys.exit(main())
