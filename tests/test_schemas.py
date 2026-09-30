"""Negative and positive schema validation tests.

Validates agent.yaml and policy.yaml against JSON Schemas, plus
provenance schema correctness. Catches schema drift (e.g., missing
enum values, type mismatches) that structural checks alone miss.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, ValidationError, validate

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"
AGENTS_DIR = REPO_ROOT / "agents"


@pytest.fixture
def agent_schema() -> dict:
    with open(SCHEMAS_DIR / "agent.schema.json") as f:
        return json.load(f)


@pytest.fixture
def policy_schema() -> dict:
    with open(SCHEMAS_DIR / "policy.schema.json") as f:
        return json.load(f)


@pytest.fixture
def provenance_schema() -> dict:
    with open(SCHEMAS_DIR / "provenance.schema.json") as f:
        return json.load(f)


def _load_agent_yamls() -> list[tuple[str, dict]]:
    """Load all agent.yaml files as (agent_name, data) pairs."""
    results = []
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue
        agent_file = agent_dir / "agent.yaml"
        if agent_file.exists():
            with open(agent_file) as f:
                results.append((agent_dir.name, yaml.safe_load(f)))
    return results


def _load_policy_yamls() -> list[tuple[str, dict]]:
    """Load all policy.yaml files as (agent_name, data) pairs."""
    results = []
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue
        policy_file = agent_dir / "policy.yaml"
        if policy_file.exists():
            with open(policy_file) as f:
                results.append((agent_dir.name, yaml.safe_load(f)))
    return results


# --- Positive tests: all real agent files must validate ---


class TestAgentSchemaPositive:
    """Every real agent.yaml must pass schema validation."""

    @pytest.mark.parametrize(
        "name,data",
        _load_agent_yamls(),
        ids=[n for n, _ in _load_agent_yamls()],
    )
    def test_agent_yaml_validates(self, name: str, data: dict, agent_schema: dict):
        validate(instance=data, schema=agent_schema, cls=Draft202012Validator)


class TestPolicySchemaPositive:
    """Every real policy.yaml must pass schema validation."""

    @pytest.mark.parametrize(
        "name,data",
        _load_policy_yamls(),
        ids=[n for n, _ in _load_policy_yamls()],
    )
    def test_policy_yaml_validates(self, name: str, data: dict, policy_schema: dict):
        validate(instance=data, schema=policy_schema, cls=Draft202012Validator)


# --- Negative tests: invalid data must fail schema validation ---


class TestAgentSchemaNegative:
    """Invalid agent.yaml documents must be rejected by the schema."""

    def test_missing_identity_tag(self, agent_schema: dict):
        data = {
            "name": "test",
            "description": "test",
            "model_policy": {"provider": None, "model": None},
        }
        with pytest.raises(ValidationError, match="identity_tag"):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_missing_name(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:jolarca:test",
            "description": "test",
            "model_policy": {"provider": None, "model": None},
        }
        with pytest.raises(ValidationError, match="name"):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_missing_description(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:jolarca:test",
            "name": "test",
            "model_policy": {"provider": None, "model": None},
        }
        with pytest.raises(ValidationError, match="description"):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_missing_model_policy(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:jolarca:test",
            "name": "test",
            "description": "test",
        }
        with pytest.raises(ValidationError, match="model_policy"):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_invalid_identity_tag_pattern(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:wrong-prefix:test",
            "name": "test",
            "description": "test",
            "model_policy": {"provider": None, "model": None},
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_invalid_identity_tag_uppercase(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:jolarca:MyAgent",
            "name": "test",
            "description": "test",
            "model_policy": {"provider": None, "model": None},
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_invalid_data_classification(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:jolarca:test",
            "name": "test",
            "description": "test",
            "data_classification": "secret",
            "model_policy": {"provider": None, "model": None},
        }
        with pytest.raises(ValidationError, match="data_classification"):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_invalid_human_gate(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:jolarca:test",
            "name": "test",
            "description": "test",
            "model_policy": {"provider": None, "model": None},
            "human_gate": "auto_approve",
        }
        with pytest.raises(ValidationError, match="human_gate"):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_additional_properties_rejected(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:jolarca:test",
            "name": "test",
            "description": "test",
            "model_policy": {"provider": None, "model": None},
            "unknown_field": "value",
        }
        with pytest.raises(ValidationError, match="unknown_field"):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_model_policy_missing_provider(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:jolarca:test",
            "name": "test",
            "description": "test",
            "model_policy": {"model": None},
        }
        with pytest.raises(ValidationError, match="provider"):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_model_policy_missing_model(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:jolarca:test",
            "name": "test",
            "description": "test",
            "model_policy": {"provider": None},
        }
        with pytest.raises(ValidationError, match="model"):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_layer_must_be_integer(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:jolarca:test",
            "name": "test",
            "description": "test",
            "layer": "zero",
            "model_policy": {"provider": None, "model": None},
        }
        with pytest.raises(ValidationError, match="layer"):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)

    def test_temperature_out_of_range(self, agent_schema: dict):
        data = {
            "identity_tag": "agent:jolarca:test",
            "name": "test",
            "description": "test",
            "model_policy": {"provider": None, "model": None, "temperature": 5.0},
        }
        with pytest.raises(ValidationError, match="temperature"):
            validate(instance=data, schema=agent_schema, cls=Draft202012Validator)


class TestPolicySchemaNegative:
    """Invalid policy.yaml documents must be rejected by the schema."""

    def test_missing_allow(self, policy_schema: dict):
        data = {"deny": {"actions": ["bad_thing"]}}
        with pytest.raises(ValidationError, match="allow"):
            validate(instance=data, schema=policy_schema, cls=Draft202012Validator)

    def test_missing_deny(self, policy_schema: dict):
        data = {"allow": {"actions": ["good_thing"]}}
        with pytest.raises(ValidationError, match="deny"):
            validate(instance=data, schema=policy_schema, cls=Draft202012Validator)

    def test_additional_properties_rejected(self, policy_schema: dict):
        data = {
            "allow": {"actions": ["good"]},
            "deny": {"actions": ["bad"]},
            "unknown_section": {"key": "value"},
        }
        with pytest.raises(ValidationError, match="unknown_section"):
            validate(instance=data, schema=policy_schema, cls=Draft202012Validator)

    def test_escalation_invalid_action(self, policy_schema: dict):
        data = {
            "allow": {},
            "deny": {},
            "escalation": {"patterns": ["test"], "action": "ignore"},
        }
        with pytest.raises(ValidationError, match="action"):
            validate(instance=data, schema=policy_schema, cls=Draft202012Validator)

    def test_retention_zero_days_rejected(self, policy_schema: dict):
        data = {
            "allow": {},
            "deny": {},
            "retention": {"max_days": 0},
        }
        with pytest.raises(ValidationError, match="max_days"):
            validate(instance=data, schema=policy_schema, cls=Draft202012Validator)

    def test_budget_negative_cost_rejected(self, policy_schema: dict):
        data = {
            "allow": {},
            "deny": {},
            "budget": {"max_cost_per_day_usd": -10},
        }
        with pytest.raises(ValidationError, match="max_cost_per_day_usd"):
            validate(instance=data, schema=policy_schema, cls=Draft202012Validator)

    def test_retention_invalid_log_level(self, policy_schema: dict):
        data = {
            "allow": {},
            "deny": {},
            "retention": {"log_level": "verbose"},
        }
        with pytest.raises(ValidationError, match="log_level"):
            validate(instance=data, schema=policy_schema, cls=Draft202012Validator)


class TestProvenanceSchema:
    """Provenance schema must accept valid records and reject invalid ones."""

    def test_valid_provenance_record(self, provenance_schema: dict):
        record = {
            "claim_id": "claim-001",
            "agent_tag": "agent:jolarca:content",
            "sources": [
                {
                    "source_id": "jolarca-docs",
                    "source_type": "approved_document",
                    "excerpt": "Test excerpt",
                    "confidence": 0.95,
                }
            ],
            "timestamp": "2026-10-01T12:00:00Z",
            "tenant_id": "tenant-a",
            "locale": "en",
        }
        validate(instance=record, schema=provenance_schema, cls=Draft202012Validator)

    def test_missing_claim_id(self, provenance_schema: dict):
        record = {
            "agent_tag": "agent:jolarca:content",
            "sources": [{"source_id": "s1", "source_type": "approved_document"}],
            "timestamp": "2026-10-01T12:00:00Z",
        }
        with pytest.raises(ValidationError, match="claim_id"):
            validate(instance=record, schema=provenance_schema, cls=Draft202012Validator)

    def test_missing_agent_tag(self, provenance_schema: dict):
        record = {
            "claim_id": "claim-001",
            "sources": [{"source_id": "s1", "source_type": "approved_document"}],
            "timestamp": "2026-10-01T12:00:00Z",
        }
        with pytest.raises(ValidationError, match="agent_tag"):
            validate(instance=record, schema=provenance_schema, cls=Draft202012Validator)

    def test_missing_sources(self, provenance_schema: dict):
        record = {
            "claim_id": "claim-001",
            "agent_tag": "agent:jolarca:content",
            "timestamp": "2026-10-01T12:00:00Z",
        }
        with pytest.raises(ValidationError, match="sources"):
            validate(instance=record, schema=provenance_schema, cls=Draft202012Validator)

    def test_empty_sources_rejected(self, provenance_schema: dict):
        record = {
            "claim_id": "claim-001",
            "agent_tag": "agent:jolarca:content",
            "sources": [],
            "timestamp": "2026-10-01T12:00:00Z",
        }
        with pytest.raises(ValidationError, match="sources"):
            validate(instance=record, schema=provenance_schema, cls=Draft202012Validator)

    def test_missing_timestamp(self, provenance_schema: dict):
        record = {
            "claim_id": "claim-001",
            "agent_tag": "agent:jolarca:content",
            "sources": [{"source_id": "s1", "source_type": "approved_document"}],
        }
        with pytest.raises(ValidationError, match="timestamp"):
            validate(instance=record, schema=provenance_schema, cls=Draft202012Validator)

    def test_invalid_agent_tag_pattern(self, provenance_schema: dict):
        record = {
            "claim_id": "claim-001",
            "agent_tag": "agent:wrong:tag",
            "sources": [{"source_id": "s1", "source_type": "approved_document"}],
            "timestamp": "2026-10-01T12:00:00Z",
        }
        with pytest.raises(ValidationError):
            validate(instance=record, schema=provenance_schema, cls=Draft202012Validator)

    def test_invalid_source_type(self, provenance_schema: dict):
        record = {
            "claim_id": "claim-001",
            "agent_tag": "agent:jolarca:content",
            "sources": [{"source_id": "s1", "source_type": "random_website"}],
            "timestamp": "2026-10-01T12:00:00Z",
        }
        with pytest.raises(ValidationError, match="source_type"):
            validate(instance=record, schema=provenance_schema, cls=Draft202012Validator)

    def test_confidence_out_of_range(self, provenance_schema: dict):
        record = {
            "claim_id": "claim-001",
            "agent_tag": "agent:jolarca:content",
            "sources": [
                {
                    "source_id": "s1",
                    "source_type": "approved_document",
                    "confidence": 1.5,
                }
            ],
            "timestamp": "2026-10-01T12:00:00Z",
        }
        with pytest.raises(ValidationError, match="confidence"):
            validate(instance=record, schema=provenance_schema, cls=Draft202012Validator)

    def test_additional_properties_rejected(self, provenance_schema: dict):
        record = {
            "claim_id": "claim-001",
            "agent_tag": "agent:jolarca:content",
            "sources": [{"source_id": "s1", "source_type": "approved_document"}],
            "timestamp": "2026-10-01T12:00:00Z",
            "extra_field": "not allowed",
        }
        with pytest.raises(ValidationError, match="extra_field"):
            validate(instance=record, schema=provenance_schema, cls=Draft202012Validator)
