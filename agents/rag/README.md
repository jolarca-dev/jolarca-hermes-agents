# RAG Agent

**Identity tag:** `agent:jolarca:rag`
**Layer:** 2 (data access + compliance)
**Data classification:** confidential

## Purpose

Approved-source retrieval, tenant/locale-scoped index access for the Hermes
agent fleet.

## Responsibilities

- Retrieve documents from approved sources only
- Enforce tenant isolation (no cross-tenant access)
- Scope queries by locale
- Log all retrieval events

## Dependencies

- `guardrails` (Layer 1)

## Policy

See `policy.yaml` for allow/deny rules, escalation patterns, and retention.

## Tests

Run: `pytest agents/rag/tests/`
