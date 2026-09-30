#!/usr/bin/env python3
"""C11/C12: Validate the declarative evaluation suite.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.

Enforces two properties of evaluations/**/cases.yaml:
  * Grounding — every case maps to a real entry in the referenced agent's
    policy.yaml (escalation pattern, deny action/resource, or allow action), so
    an eval case can never drift from the policy it claims to exercise.
  * Coverage — the suite set collectively covers the controls evaluations are
    responsible for strengthening (C11 PII redaction, C12 injection defence).

Schema conformance is validated separately by tests/test_eval_cases.py against
schemas/eval-case.schema.json. No model provider is registered yet (C13
deferred), so these are static fixtures a live harness will replay later.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_DIR = BASE_DIR / "evaluations"
AGENTS_DIR = BASE_DIR / "agents"

# Controls the evaluation suite must collectively cover.
REQUIRED_CONTROLS = {"C11", "C12"}

# Keys every case must declare (schema conformance is checked in tests/).
REQUIRED_CASE_KEYS = ("id", "input", "expected_action", "maps_to", "control")


def policy_entries(agent: str) -> set[str] | None:
    """Return every string entry declared in an agent's policy.yaml, or None if absent."""
    policy_file = AGENTS_DIR / agent / "policy.yaml"
    if not policy_file.exists():
        return None
    with open(policy_file) as f:
        policy = yaml.safe_load(f) or {}
    entries: set[str] = set()
    for section in ("allow", "deny"):
        block = policy.get(section) or {}
        for values in block.values():
            if isinstance(values, list):
                entries.update(str(v) for v in values)
    escalation = policy.get("escalation") or {}
    entries.update(str(p) for p in (escalation.get("patterns") or []))
    return entries


def load_suites() -> list[tuple[Path, dict]]:
    """Load every evaluations/**/cases.yaml as (path, data) pairs."""
    suites: list[tuple[Path, dict]] = []
    for cases_file in sorted(EVAL_DIR.rglob("cases.yaml")):
        with open(cases_file) as f:
            suites.append((cases_file, yaml.safe_load(f) or {}))
    return suites


def main() -> int:
    if not EVAL_DIR.is_dir():
        print(f"FAILED — evaluations directory not found: {EVAL_DIR}", file=sys.stderr)
        return 1

    errors: list[str] = []
    covered: set[str] = set()
    entry_cache: dict[str, set[str] | None] = {}
    case_count = 0

    suites = load_suites()
    if not suites:
        errors.append("no evaluations/**/cases.yaml suites found")

    for cases_file, suite in suites:
        rel = cases_file.relative_to(BASE_DIR)
        cases = suite.get("cases")
        if not isinstance(cases, list) or not cases:
            errors.append(f"{rel}: missing or empty 'cases' list")
            continue
        for case in cases:
            case_count += 1
            label = f"{rel}#{case.get('id', '?')}"
            for key in REQUIRED_CASE_KEYS:
                if key not in case:
                    errors.append(f"{label}: missing required key '{key}'")
            control = case.get("control")
            if isinstance(control, str):
                covered.add(control)
            maps_to = case.get("maps_to") or {}
            agent = maps_to.get("agent")
            entry = maps_to.get("entry")
            if not agent or not entry:
                errors.append(f"{label}: maps_to requires 'agent' and 'entry'")
                continue
            if agent not in entry_cache:
                entry_cache[agent] = policy_entries(agent)
            known = entry_cache[agent]
            if known is None:
                errors.append(f"{label}: unknown agent '{agent}' (no policy.yaml)")
            elif entry not in known:
                errors.append(f"{label}: entry '{entry}' not found in agents/{agent}/policy.yaml")

    missing = REQUIRED_CONTROLS - covered
    if missing:
        errors.append(f"suite does not cover required control(s): {', '.join(sorted(missing))}")

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print(
        f"PASSED — check_eval_coverage: {case_count} case(s) across {len(suites)} suite(s); "
        f"controls covered: {', '.join(sorted(covered))}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
