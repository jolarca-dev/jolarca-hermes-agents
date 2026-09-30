"""Tests for the content agent."""

from pathlib import Path

import yaml

AGENT_DIR = Path(__file__).resolve().parent.parent


def test_agent_yaml_valid():
    """agent.yaml is valid YAML with required fields."""
    with open(AGENT_DIR / "agent.yaml") as f:
        data = yaml.safe_load(f)
    assert data["identity_tag"] == "agent:jolarca:content"
    assert data["layer"] == 3
    assert "rag" in data["depends_on"]
    assert "guardrails" in data["depends_on"]
    assert data["data_classification"] == "confidential"
    assert data["human_gate"] == "editorial"


def test_policy_yaml_valid():
    """policy.yaml is valid YAML with allow and deny sections."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert "allow" in data
    assert "deny" in data


def test_deny_contains_publication_without_approval():
    """Policy denies publishing without editorial approval."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_actions = data["deny"]["actions"]
    assert "publish_without_approval" in deny_actions
    assert "use_unapproved_sources" in deny_actions


def test_escalation_contains_provenance():
    """Escalation patterns include provenance checks."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    patterns = data["escalation"]["patterns"]
    assert "provenance_missing" in patterns
