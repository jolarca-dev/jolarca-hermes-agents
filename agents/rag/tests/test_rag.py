"""Tests for the RAG agent."""

from pathlib import Path

import yaml

AGENT_DIR = Path(__file__).resolve().parent.parent


def test_agent_yaml_valid():
    """agent.yaml is valid YAML with required fields."""
    with open(AGENT_DIR / "agent.yaml") as f:
        data = yaml.safe_load(f)
    assert data["identity_tag"] == "agent:jolarca:rag"
    assert data["layer"] == 2
    assert "guardrails" in data["depends_on"]
    assert data["data_classification"] == "confidential"


def test_policy_yaml_valid():
    """policy.yaml is valid YAML with allow and deny sections."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    assert "allow" in data
    assert "deny" in data


def test_deny_contains_tenant_isolation():
    """Policy denies cross-tenant index access."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_actions = data["deny"]["actions"]
    assert "cross_tenant_index_access" in deny_actions
    assert "unapproved_source_retrieval" in deny_actions


def test_deny_contains_mission_patterns():
    """Policy denies mission-platform references (ADR-0004 R4)."""
    with open(AGENT_DIR / "policy.yaml") as f:
        data = yaml.safe_load(f)
    deny_resources = data["deny"]["resources"]
    assert any("jol-" in r for r in deny_resources)
