# Observability Agent

**Identity tag:** `agent:jolarca:observability`
**Layer:** 0 (cross-cutting, spans all layers)
**Data classification:** internal

## Purpose

Model/eval drift, token+cost telemetry, incident signals for the Hermes agent
fleet.

## Responsibilities

- Collect telemetry (tokens, cost, latency)
- Detect model/eval drift
- Emit incident signals when thresholds exceeded
- Aggregate metrics by agent, tenant, time window

## Dependencies

None (cross-cutting, spans all layers).

## Policy

See `policy.yaml` for allow/deny rules, escalation patterns, and retention.

## Tests

Run: `pytest agents/observability/tests/`
