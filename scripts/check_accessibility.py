#!/usr/bin/env python3
"""C6: Validate accessibility agent gate and WCAG deny rules.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    errors: list[str] = []

    # accessibility agent must have blocks_release gate
    agent_file = BASE_DIR / "agents" / "accessibility" / "agent.yaml"
    if not agent_file.exists():
        print(f"FAILED — {agent_file} not found", file=sys.stderr)
        return 1

    with open(agent_file) as f:
        agent = yaml.safe_load(f)

    if agent.get("human_gate") != "blocks_release":
        errors.append(f"accessibility human_gate is '{agent.get('human_gate')}', expected 'blocks_release'")

    # accessibility policy must deny bypassing WCAG checks
    policy_file = BASE_DIR / "agents" / "accessibility" / "policy.yaml"
    if not policy_file.exists():
        print(f"FAILED — {policy_file} not found", file=sys.stderr)
        return 1

    with open(policy_file) as f:
        policy = yaml.safe_load(f)

    deny_actions = policy.get("deny", {}).get("actions", [])
    if "bypass_wcag_checks" not in deny_actions:
        errors.append("accessibility policy missing deny action: bypass_wcag_checks")

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print("PASSED — check_accessibility")
    return 0


if __name__ == "__main__":
    sys.exit(main())
