"""Tests for the observability agent."""

from pathlib import Path

import yaml

AGENT_DIR = Path(__file__).resolve().parent.parent


def test_agent_yaml_valid():
    """agent.yaml is valid YAML with required fields."""
    with open(AGENT_DIR / "agent.yaml") as f:
        data = yaml.safe_load(f)
    assert data["identity_tag"] == "agent:jolarca:observability"
    assert data["layer"] == 0
    assert data["depends_on"] == []
    assert data["data_classification"] == "internal"


def test_policy_yaml_valid():
    """policy.yaml is valid YAML with allow and deny sections."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert "allow" in data
    assert "deny" in data


def test_deny_contains_telemetry_tampering():
    """Policy denies telemetry modification and signal suppression."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_actions = data["deny"]["actions"]
    assert "modify_telemetry" in deny_actions
    assert "suppress_incident_signals" in deny_actions


def test_escalation_patterns_defined():
    """Escalation patterns include drift and cost signals."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    patterns = data["escalation"]["patterns"]
    assert any("drift" in p for p in patterns)
    assert any("cost" in p for p in patterns)
