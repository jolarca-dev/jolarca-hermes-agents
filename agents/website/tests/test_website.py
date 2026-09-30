"""Tests for the website agent."""

from pathlib import Path

import yaml

AGENT_DIR = Path(__file__).resolve().parent.parent


def test_agent_yaml_valid():
    """agent.yaml is valid YAML with required fields."""
    with open(AGENT_DIR / "agent.yaml") as f:
        data = yaml.safe_load(f)
    assert data["identity_tag"] == "agent:jolarca:website"
    assert data["layer"] == 6
    assert "editorial" in data["depends_on"]
    assert "accessibility" in data["depends_on"]
    assert data["data_classification"] == "public"
    assert data["human_gate"] == "editorial"


def test_policy_yaml_valid():
    """policy.yaml is valid YAML with allow and deny sections."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert "allow" in data
    assert "deny" in data


def test_deny_contains_unapproved_content():
    """Policy denies using unapproved content and bypassing gates."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_actions = data["deny"]["actions"]
    assert "use_unapproved_content" in deny_actions
    assert "bypass_accessibility_gate" in deny_actions


def test_escalation_contains_gate_failures():
    """Escalation patterns include gate failures."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    patterns = data["escalation"]["patterns"]
    assert "unapproved_content_requested" in patterns
    assert "accessibility_gate_failed" in patterns
