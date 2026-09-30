# Consent Agent

**Identity tag:** `agent:jolarca:consent`
**Layer:** 2 (data access + compliance)
**Data classification:** restricted
**Human gate:** blocks_all

## Purpose

PII detection/redaction, DSAR support, purpose-limitation checks for the
Hermes agent fleet.

## Responsibilities

- Detect PII in inputs and outputs
- Redact PII before passing to other agents
- Support Data Subject Access Requests (DSAR)
- Enforce purpose limitation
- Ensure tenant isolation for PII

## Dependencies

- `guardrails` (Layer 1)

## Policy

See `policy.yaml` for allow/deny rules, escalation patterns, and retention.

## Tests

Run: `pytest agents/consent/tests/`
