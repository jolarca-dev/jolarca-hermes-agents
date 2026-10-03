#!/usr/bin/env python3
"""Validate agent.yaml and policy.yaml structure and identity tags.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.

Checks enforced here, hand-rolled rather than schema-driven:
  * agent.yaml exists, parses as YAML, and has a mapping at the root
  * policy.yaml exists, parses as YAML, and has a mapping at the root
  * the required keys are present in each file
  * identity_tag matches the pattern agent:jolarca:<module-id>
  * identity_tag is unique across all agents

Full JSON Schema (Draft 2020-12) conformance is asserted elsewhere, in
tests/test_schemas.py, which runs in the CI `test` job and not here. The two
checks are complementary, not equivalent: a document that passes this script can
still violate schemas/agent.schema.json.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
AGENTS_DIR = BASE_DIR / "agents"

IDENTITY_TAG_RE = re.compile(r"^agent:jolarca:[a-z][a-z0-9-]*$")


def validate_agent(agent_dir: Path) -> list[str]:
    errors: list[str] = []
    name = agent_dir.name

    # agent.yaml
    agent_file = agent_dir / "agent.yaml"
    if not agent_file.exists():
        errors.append(f"{name}: missing agent.yaml")
        return errors

    with open(agent_file) as f:
        try:
            agent = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"{name}: invalid YAML in agent.yaml — {e}")
            return errors

    if not isinstance(agent, dict):
        errors.append(f"{name}: agent.yaml root must be a mapping")
        return errors

    # Required fields
    for field in ["identity_tag", "name", "description", "model_policy"]:
        if field not in agent:
            errors.append(f"{name}: agent.yaml missing required field '{field}'")

    # Identity tag format
    tag = agent.get("identity_tag", "")
    if not IDENTITY_TAG_RE.match(tag):
        errors.append(
            f"{name}: identity_tag '{tag}' does not match "
            f"agent:jolarca:<module-id> pattern"
        )

    # policy.yaml
    policy_file = agent_dir / "policy.yaml"
    if not policy_file.exists():
        errors.append(f"{name}: missing policy.yaml")
        return errors

    with open(policy_file) as f:
        try:
            policy = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"{name}: invalid YAML in policy.yaml — {e}")
            return errors

    if not isinstance(policy, dict):
        errors.append(f"{name}: policy.yaml root must be a mapping")
        return errors

    for field in ["allow", "deny"]:
        if field not in policy:
            errors.append(f"{name}: policy.yaml missing required field '{field}'")

    return errors


def main() -> int:
    if not AGENTS_DIR.is_dir():
        print(f"ERROR: agents directory not found: {AGENTS_DIR}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    seen_tags: dict[str, str] = {}
    agent_count = 0

    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue
        agent_count += 1
        errors = validate_agent(agent_dir)
        all_errors.extend(errors)

        # Check tag uniqueness
        agent_file = agent_dir / "agent.yaml"
        if agent_file.exists():
            with open(agent_file) as f:
                data = yaml.safe_load(f)
            tag = data.get("identity_tag", "")
            if tag in seen_tags:
                all_errors.append(
                    f"{agent_dir.name}: duplicate identity_tag '{tag}' "
                    f"(also used by {seen_tags[tag]})"
                )
            seen_tags[tag] = agent_dir.name

    if all_errors:
        print(f"FAILED — {len(all_errors)} error(s) in {agent_count} agent(s):\n")
        for err in all_errors:
            print(f"  x {err}")
        return 1

    print(f"PASSED — {agent_count} agent(s) validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
