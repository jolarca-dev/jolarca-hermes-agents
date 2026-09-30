# Accessibility Agent

**Identity tag:** `agent:jolarca:accessibility`
**Layer:** 4 (specialization)
**Data classification:** public
**Human gate:** blocks_release

## Purpose

WCAG validation, release gate for the Hermes agent fleet.

## Responsibilities

- Validate WCAG 2.1 AA compliance
- Check alt text for all images
- Check color contrast for all text
- Block release if violations detected
- Log all accessibility checks

## Dependencies

- `content` (Layer 3)

## Policy

See `policy.yaml` for allow/deny rules, escalation patterns, and retention.

## Tests

Run: `pytest agents/accessibility/tests/`
