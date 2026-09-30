"""Tests for the guardrails agent."""

from pathlib import Path

import yaml

AGENT_DIR = Path(__file__).resolve().parent.parent


def test_agent_yaml_valid():
    """agent.yaml is valid YAML with required fields."""
    with open(AGENT_DIR / "agent.yaml") as f:
        data = yaml.safe_load(f)
    assert data["identity_tag"] == "agent:jolarca:guardrails"
    assert data["layer"] == 1
    assert "orchestrator" in data["depends_on"]
    assert data["human_gate"] == "blocks_all"


def test_policy_yaml_valid():
    """policy.yaml is valid YAML with allow and deny sections."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert "allow" in data
    assert "deny" in data


def test_escalation_patterns_defined():
    """Escalation patterns include doctrinal and injection patterns."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    patterns = data["escalation"]["patterns"]
    assert any("doctrinal" in p for p in patterns)
    assert any("pastoral" in p for p in patterns)
    assert any("injection" in p for p in patterns)
    assert data["escalation"]["action"] == "block"


def test_deny_contains_mission_patterns():
    """Policy denies mission-platform references (ADR-0004 R4)."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_resources = data["deny"]["resources"]
    assert any("jol-" in r for r in deny_resources)


def test_guardrails_does_not_generate():
    """Guardrails agent denies content generation."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_actions = data["deny"]["actions"]
    assert "generate_content" in deny_actions
    assert "modify_content" in deny_actions
