# Editorial Agent

**Identity tag:** `agent:jolarca:editorial`
**Layer:** 5 (approval)
**Data classification:** confidential
**Human gate:** human_approver

## Purpose

Approval workflow, provenance completeness check for the Hermes agent fleet.

## Responsibilities

- Approve or reject content before publication
- Verify provenance completeness (every claim has a citation)
- Escalate doctrinal/sensitive content to human
- Log all approval decisions
- Retain records for 7 years

## Dependencies

- `content` (Layer 3) — submits drafts for approval
- `translation` (Layer 4) — submits translated content for approval

## Policy

See `policy.yaml` for allow/deny rules, escalation patterns, and retention.

## Tests

Run: `pytest agents/editorial/tests/`
