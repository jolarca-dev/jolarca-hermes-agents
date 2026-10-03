"""Guard that no agent holds a tool its own policy does not permit.

`tool_grants` (in `agent.yaml`) and `allow.actions` (in `policy.yaml`) are two views
of one least-privilege decision, and nothing previously related them: a tool could be
granted while the same agent's policy did not allow it, and `make check` would pass.

The invariant asserted here is **one-way**, deliberately. Measured across the fleet:
only `orchestrator` has the two sets equal; for the other eleven `tool_grants` is a
strict subset of `allow.actions`. Asserting equality would therefore fail eleven of
twelve agents and would state the wrong rule — least privilege is breached by a grant
the policy does not permit, never by a permitted action the agent was simply never
given as a callable tool.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"


def _rows() -> list[tuple[str, set[str], set[str]]]:
    """(agent name, granted tools, policy-allowed actions) for every agent."""
    rows: list[tuple[str, set[str], set[str]]] = []
    for agent_file in sorted(AGENTS_DIR.glob("*/agent.yaml")):
        grants = set((yaml.safe_load(agent_file.read_text(encoding="utf-8")) or {}).get("tool_grants") or [])
        policy = agent_file.parent / "policy.yaml"
        doc = yaml.safe_load(policy.read_text(encoding="utf-8")) if policy.exists() else {}
        allowed = set((doc.get("allow") or {}).get("actions") or [])
        rows.append((agent_file.parent.name, grants, allowed))
    return rows


def test_every_granted_tool_is_permitted_by_that_agent_policy():
    violations = [
        f"{name}: granted but not allowed = {sorted(grants - allowed)}"
        for name, grants, allowed in _rows()
        if grants - allowed
    ]
    assert not violations, f"tool grant escapes its own policy allow-list: {violations}"


def test_no_agent_has_an_empty_grant_or_allow_set():
    """An empty allow list would make the subset assertion pass vacuously."""
    empty = [
        f"{name} (grants={len(grants)}, allow={len(allowed)})"
        for name, grants, allowed in _rows()
        if not grants or not allowed
    ]
    assert not empty, f"agent with empty tool_grants or allow.actions: {empty}"


def test_guard_is_not_vacuous():
    """If the parser found nothing, every assertion above would pass trivially."""
    rows = _rows()
    assert len(rows) == 12, f"parsed {len(rows)} agents, expected 12"
    assert sum(len(grants) for _, grants, _ in rows) >= 40, "tool_grants total implausibly low"
