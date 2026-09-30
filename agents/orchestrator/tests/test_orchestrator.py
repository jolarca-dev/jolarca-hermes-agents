"""Tests for the orchestrator agent."""

from pathlib import Path

import yaml

AGENT_DIR = Path(__file__).resolve().parent.parent


def test_agent_yaml_valid():
    """agent.yaml is valid YAML with required fields."""
    with open(AGENT_DIR / "agent.yaml") as f:
        data = yaml.safe_load(f)
    assert data["identity_tag"] == "agent:jolarca:orchestrator"
    assert data["layer"] == 0
    assert data["depends_on"] == []
    assert data["data_classification"] == "internal"


def test_policy_yaml_valid():
    """policy.yaml is valid YAML with allow and deny sections."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert "allow" in data
    assert "deny" in data
    assert "actions" in data["deny"]
    assert "resources" in data["deny"]


def test_deny_contains_mission_patterns():
    """Policy denies mission-platform references (ADR-0004 R4)."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_resources = data["deny"]["resources"]
    assert any("jol-" in r for r in deny_resources)
    assert any("journeyoflife-org" in r for r in deny_resources)


def test_budget_defined():
    """Budget caps are defined."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert "budget" in data
    assert "max_tokens_per_request" in data["budget"]
    assert "max_tokens_per_day" in data["budget"]
