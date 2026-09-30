#!/usr/bin/env python3
"""C7: Validate that the guardrails agent has doctrinal escalation rules.

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

    # guardrails must have escalation patterns for doctrinal content
    escalation = policy.get("escalation", {})
    patterns = escalation.get("patterns", [])
    if not patterns:
        errors.append("guardrails policy missing escalation patterns")

    action = escalation.get("action", "")
    if action != "block":
        errors.append(f"guardrails escalation action is '{action}', expected 'block'")

    # guardrails must have blocks_all gate
    agent_file = BASE_DIR / "agents" / "guardrails" / "agent.yaml"
    if agent_file.exists():
        with open(agent_file) as f:
            agent = yaml.safe_load(f)
        if agent.get("human_gate") != "blocks_all":
            errors.append(f"guardrails human_gate is '{agent.get('human_gate')}', expected 'blocks_all'")

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print("PASSED — check_doctrine_escalation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
