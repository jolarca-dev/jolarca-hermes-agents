"""Tests for the audit agent."""

from pathlib import Path

import yaml

AGENT_DIR = Path(__file__).resolve().parent.parent


def test_agent_yaml_valid():
    """agent.yaml is valid YAML with required fields."""
    with open(AGENT_DIR / "agent.yaml") as f:
        data = yaml.safe_load(f)
    assert data["identity_tag"] == "agent:jolarca:audit"
    assert data["layer"] == 0
    assert data["depends_on"] == []
    assert data["data_classification"] == "confidential"


def test_policy_yaml_valid():
    """policy.yaml is valid YAML with allow and deny sections."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert "allow" in data
    assert "deny" in data


def test_deny_contains_audit_tampering():
    """Policy denies audit log modification and deletion."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_actions = data["deny"]["actions"]
    assert "modify_audit_log" in deny_actions
    assert "delete_audit_log" in deny_actions


def test_retention_is_7_years():
    """Audit logs are retained for 7 years (2555 days)."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert data["retention"]["max_days"] == 2555
