"""Tests for the editorial agent."""

from pathlib import Path

import yaml

AGENT_DIR = Path(__file__).resolve().parent.parent


def test_agent_yaml_valid():
    """agent.yaml is valid YAML with required fields."""
    with open(AGENT_DIR / "agent.yaml") as f:
        data = yaml.safe_load(f)
    assert data["identity_tag"] == "agent:jolarca:editorial"
    assert data["layer"] == 5
    assert "content" in data["depends_on"]
    assert "translation" in data["depends_on"]
    assert data["data_classification"] == "confidential"
    assert data["human_gate"] == "human_approver"


def test_policy_yaml_valid():
    """policy.yaml is valid YAML with allow and deny sections."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert "allow" in data
    assert "deny" in data


def test_deny_contains_approval_without_provenance():
    """Policy denies approving without provenance."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_actions = data["deny"]["actions"]
    assert "approve_without_provenance" in deny_actions
    assert "generate_content" in deny_actions


def test_retention_is_7_years():
    """Approval records are retained for 7 years (2555 days)."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert data["retention"]["max_days"] == 2555


def test_escalation_contains_doctrinal():
    """Escalation patterns include doctrinal content."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    patterns = data["escalation"]["patterns"]
    assert "doctrinal_content_detected" in patterns
    assert "provenance_incomplete" in patterns
