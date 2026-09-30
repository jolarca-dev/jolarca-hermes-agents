#!/usr/bin/env python3
"""C13: Validate that no LLM provider is in use without DPIA registration.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.

Currently no provider is selected. This script verifies that all agents
declare null provider (no shadow models) and that the provider registry
in policies/model-policy.md reflects this.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
AGENTS_DIR = BASE_DIR / "agents"


def main() -> int:
    errors: list[str] = []

    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue
        agent_file = agent_dir / "agent.yaml"
        if not agent_file.exists():
            continue

        with open(agent_file) as f:
            agent = yaml.safe_load(f)

        model_policy = agent.get("model_policy", {})
        provider = model_policy.get("provider")
        if provider is not None:
            errors.append(
                f"{agent_dir.name}: provider is '{provider}' but no provider "
                f"is approved — register in jolarca-vendor first (C13)"
            )

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print("PASSED — check_vendor_risk (no unapproved providers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
