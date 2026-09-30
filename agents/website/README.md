# Website Agent

**Identity tag:** `agent:jolarca:website`
**Layer:** 6 (composition)
**Data classification:** public
**Human gate:** editorial

## Purpose

Site composition from approved, gated artefacts for the Hermes agent fleet.

## Responsibilities

- Compose web pages from approved content artefacts
- Verify editorial approval for each artefact
- Verify accessibility gate passed for each artefact
- Request editorial approval for composed pages
- Log all composition events

## Dependencies

- `editorial` (Layer 5) — provides content approval
- `accessibility` (Layer 4) — provides WCAG gate

## Policy

See `policy.yaml` for allow/deny rules, escalation patterns, and retention.

## Tests

Run: `pytest agents/website/tests/`
