"""Tests for the translation agent."""

from pathlib import Path

import yaml

AGENT_DIR = Path(__file__).resolve().parent.parent


def test_agent_yaml_valid():
    """agent.yaml is valid YAML with required fields."""
    with open(AGENT_DIR / "agent.yaml") as f:
        data = yaml.safe_load(f)
    assert data["identity_tag"] == "agent:jolarca:translation"
    assert data["layer"] == 4
    assert "content" in data["depends_on"]
    assert data["data_classification"] == "confidential"
    assert data["human_gate"] == "editorial"


def test_policy_yaml_valid():
    """policy.yaml is valid YAML with allow and deny sections."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert "allow" in data
    assert "deny" in data


def test_deny_contains_terminology_violation():
    """Policy denies unapproved terminology."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_actions = data["deny"]["actions"]
    assert "use_unapproved_terminology" in deny_actions


def test_escalation_contains_sensitive_content():
    """Escalation patterns include sensitive content detection."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    patterns = data["escalation"]["patterns"]
    assert "sensitive_content_detected" in patterns
