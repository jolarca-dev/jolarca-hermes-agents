# Content Agent

**Identity tag:** `agent:jolarca:content`
**Layer:** 3 (generation)
**Data classification:** confidential
**Human gate:** editorial

## Purpose

Draft generation from retrieved sources only for the Hermes agent fleet.

## Responsibilities

- Generate draft content from retrieved sources
- Attach provenance (source citations) to every claim
- Request editorial approval before publication
- Log all generation events

## Dependencies

- `rag` (Layer 2) — provides retrieved sources
- `guardrails` (Layer 1) — enforces policy

## Policy

See `policy.yaml` for allow/deny rules, escalation patterns, and retention.

## Tests

Run: `pytest agents/content/tests/`
