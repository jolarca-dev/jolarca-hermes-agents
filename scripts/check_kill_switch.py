#!/usr/bin/env python3
"""C16: Validate that the orchestrator has a kill-switch tool grant.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    agent_file = BASE_DIR / "agents" / "orchestrator" / "agent.yaml"
    if not agent_file.exists():
        print(f"FAILED — {agent_file} not found", file=sys.stderr)
        return 1

    with open(agent_file) as f:
        agent = yaml.safe_load(f)

    tool_grants = agent.get("tool_grants", [])
    if "kill_switch" not in tool_grants:
        print("FAILED — orchestrator missing tool_grant: kill_switch", file=sys.stderr)
        return 1

    print("PASSED — check_kill_switch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
