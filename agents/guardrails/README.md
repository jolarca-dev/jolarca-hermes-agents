# Guardrails Agent

**Identity tag:** `agent:jolarca:guardrails`
**Layer:** 1 (safety boundary)
**Data classification:** internal
**Human gate:** blocks_all

## Purpose

Prompt-injection defence, deny-list enforcement, and doctrinal/pastoral
escalation for the Hermes agent fleet.

## Responsibilities

- Inspect all inputs and outputs for policy violations
- Block mission-platform references (ADR-0004 R4)
- Escalate doctrinal and pastoral questions to a human
- Detect prompt injection and jailbreak attempts
- Log every violation immutably

## Dependencies

- `orchestrator` (Layer 0)

## Policy

See `policy.yaml` for allow/deny rules, escalation patterns, and retention.

## Tests

Run: `pytest agents/guardrails/tests/`
