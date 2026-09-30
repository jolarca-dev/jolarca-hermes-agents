"""Tests for the accessibility agent."""

from pathlib import Path

import yaml

AGENT_DIR = Path(__file__).resolve().parent.parent


def test_agent_yaml_valid():
    """agent.yaml is valid YAML with required fields."""
    with open(AGENT_DIR / "agent.yaml") as f:
        data = yaml.safe_load(f)
    assert data["identity_tag"] == "agent:jolarca:accessibility"
    assert data["layer"] == 4
    assert "content" in data["depends_on"]
    assert data["data_classification"] == "public"
    assert data["human_gate"] == "blocks_release"


def test_policy_yaml_valid():
    """policy.yaml is valid YAML with allow and deny sections."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert "allow" in data
    assert "deny" in data


def test_deny_contains_wcag_bypass():
    """Policy denies bypassing WCAG checks."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_actions = data["deny"]["actions"]
    assert "bypass_wcag_checks" in deny_actions


def test_escalation_contains_wcag_violation():
    """Escalation patterns include WCAG violations."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    patterns = data["escalation"]["patterns"]
    assert "wcag_violation_detected" in patterns
    assert "missing_alt_text" in patterns
