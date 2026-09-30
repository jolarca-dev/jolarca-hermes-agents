# Audit Agent

**Identity tag:** `agent:jolarca:audit`
**Layer:** 0 (cross-cutting, spans all layers)
**Data classification:** confidential

## Purpose

Immutable decision logging, evidence hashing, drift detection for the Hermes
agent fleet.

## Responsibilities

- Log all agent decisions immutably
- Hash evidence with SHA-256
- Detect drift in agent behaviour
- Maintain tamper-evident hash chain
- Retain logs for 7 years (SOC 2, ISO 27001)

## Dependencies

None (cross-cutting, spans all layers).

## Policy

See `policy.yaml` for allow/deny rules, escalation patterns, and retention.

## Tests

Run: `pytest agents/audit/tests/`
