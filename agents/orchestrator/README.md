# Orchestrator Agent

**Identity tag:** `agent:jolarca:orchestrator`
**Layer:** 0 (foundation)
**Data classification:** internal

## Purpose

Routing, delegation, budget/cost caps, and kill-switch for the Hermes agent fleet.

## Responsibilities

- Route requests to specialist agents
- Enforce token and cost budget ceilings
- Activate kill-switch to halt all operations
- Log all delegation decisions

## Dependencies

None (Layer 0 — foundation agent).

## Policy

See `policy.yaml` for allow/deny rules, budget caps, and escalation conditions.

## Tests

Run: `pytest agents/orchestrator/tests/`
