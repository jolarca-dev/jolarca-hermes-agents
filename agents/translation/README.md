# Translation Agent

**Identity tag:** `agent:jolarca:translation`
**Layer:** 4 (specialization)
**Data classification:** confidential
**Human gate:** editorial (sensitive content)

## Purpose

Locale rendering, terminology consistency for the Hermes agent fleet.

## Responsibilities

- Translate approved content into target locales
- Enforce terminology consistency
- Escalate sensitive content (liturgical, pastoral, doctrinal)
- Preserve provenance through translation
- Request editorial approval

## Dependencies

- `content` (Layer 3)

## Policy

See `policy.yaml` for allow/deny rules, escalation patterns, and retention.

## Tests

Run: `pytest agents/translation/tests/`
