"""Guard the derived tool register against arithmetic drift.

`docs/tool-register.md` states its own precedence rule — "If this register and an
`agent.yaml` disagree, the `agent.yaml` wins — update this document, never the
reverse" — but nothing enforced it, and the register drifted anyway:

  * its totals sentence claimed 39 distinct tools while its own Tool index table
    listed 38, so the document contradicted itself, not merely the code;
  * the grants total moved from 40 to 41 when the orchestrator gained
    `log_decision`, and the ADR describing the register kept saying 40.

This suite re-derives every figure from the `agent.yaml` files and asserts the
document agrees. It closes the `QODER.md` drift row "tool register lists a tool
no agent grants / an agent grants an unlisted tool -> none, manual".
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"
REGISTER = ROOT / "docs" / "tool-register.md"

# "**Totals (verified):** 41 grants across 12 agents; 38 distinct tools."
TOTALS_RE = re.compile(r"(\d+) grants across (\d+) agents; (\d+) distinct tools")
BACKTICK_RE = re.compile(r"`([^`]*)`")


def _grants_by_agent() -> dict[str, list[str]]:
    """The source of truth: every agent's declared tool_grants."""
    grants: dict[str, list[str]] = {}
    for path in sorted(AGENTS_DIR.glob("*/agent.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        module = str(doc.get("identity_tag", "")).rsplit(":", 1)[-1]
        grants[module] = list(doc.get("tool_grants") or [])
    return grants


def _register_text() -> str:
    return REGISTER.read_text(encoding="utf-8")


def _agent_rows() -> dict[str, list[str]]:
    """Parse the 'Grants by agent' table; first cell is a bare agent name."""
    names = set(_grants_by_agent())
    rows: dict[str, list[str]] = {}
    for line in _register_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[0] in names:
            rows[cells[0]] = BACKTICK_RE.findall(cells[3])
    return rows


def _indexed_tools() -> set[str]:
    """Parse the 'Tool index' table; first cell is a backticked tool name."""
    tools: set[str] = set()
    for line in _register_text().splitlines():
        if line.startswith("| `"):
            match = BACKTICK_RE.search(line)
            if match:
                tools.add(match.group(1))
    return tools


def _granted_tools() -> set[str]:
    return {tool for grants in _grants_by_agent().values() for tool in grants}


def test_totals_sentence_matches_the_fleet():
    """The one line that summarises everything else must be re-derivable."""
    grants = _grants_by_agent()
    total = sum(len(items) for items in grants.values())
    match = TOTALS_RE.search(_register_text())
    assert match, "register no longer carries the '<n> grants across <m> agents; <k> distinct tools' totals"
    stated_grants, stated_agents, stated_distinct = (int(value) for value in match.groups())
    assert stated_agents == len(grants), f"register claims {stated_agents} agents; fleet has {len(grants)}"
    assert stated_grants == total, f"register claims {stated_grants} grants; agent.yaml files declare {total}"
    assert stated_distinct == len(_granted_tools()), (
        f"register claims {stated_distinct} distinct tools; the fleet grants {len(_granted_tools())}"
    )


def test_per_agent_grants_match_every_agent_yaml():
    """An agent gaining or dropping a grant must be reflected in the register."""
    grants = _grants_by_agent()
    rows = _agent_rows()
    assert set(rows) == set(grants), (
        f"register rows and agent directories differ: "
        f"only in register={sorted(set(rows) - set(grants))}, "
        f"only on disk={sorted(set(grants) - set(rows))}"
    )
    drift = {
        agent: (sorted(grants[agent]), sorted(rows.get(agent, [])))
        for agent in grants
        if sorted(grants[agent]) != sorted(rows.get(agent, []))
    }
    assert not drift, f"'Grants by agent' disagrees with agent.yaml (disk, register): {drift}"


def test_tool_index_is_exactly_the_granted_set():
    """No phantom tool listed without a grant, no grant left unlisted."""
    granted, indexed = _granted_tools(), _indexed_tools()
    assert indexed == granted, (
        f"listed but never granted={sorted(indexed - granted)}, granted but not listed={sorted(granted - indexed)}"
    )


def test_shared_tools_are_the_actual_duplicates():
    counts = Counter(tool for grants in _grants_by_agent().values() for tool in grants)
    duplicated = {tool for tool, seen in counts.items() if seen > 1}
    match = re.search(r"shared:(.+?)\.\n", _register_text(), re.DOTALL)
    assert match, "register no longer enumerates the shared tools after 'shared:'"
    named = set(BACKTICK_RE.findall(match.group(1)))
    assert named == duplicated, f"register names shared tools {sorted(named)}; the fleet shares {sorted(duplicated)}"


def test_guard_is_not_vacuous():
    """If either parser silently stops matching, the tests above pass trivially."""
    grants = _grants_by_agent()
    assert len(grants) == 12, f"parsed {len(grants)} agent.yaml files"
    assert sum(len(items) for items in grants.values()) >= 40, "grants total implausibly low"
    assert len(_agent_rows()) == 12, "the 'Grants by agent' table was not parsed"
    assert len(_indexed_tools()) >= 35, "the 'Tool index' table was not parsed"
