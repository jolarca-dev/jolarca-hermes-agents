---
name: Agent Incident
about: Report an agent incident (hallucination, doctrine breach, policy violation, injection success)
title: '[INCIDENT] '
labels: incident, compliance
assignees: ''
---

## Incident Summary

Brief description of what occurred.

## Agent(s) Involved

- Primary agent: [e.g., guardrails, content, editorial]
- Related agents: [if any]

## Control(s) Affected

- [e.g., C7 (doctrine escalation), C11 (PII), C12 (injection defence)]

## Incident Type

- [ ] Hallucination / fabricated content
- [ ] Doctrinal or pastoral breach (C7)
- [ ] PII leak or redaction failure (C11)
- [ ] Injection defence bypass (C12)
- [ ] Policy violation (unapproved source, cross-tenant access, etc.)
- [ ] Kill-switch failure (C16)
- [ ] Other: [specify]

## Timeline

- **When detected:** [date/time]
- **When resolved:** [if applicable]
- **Detection method:** [automated check, manual review, user report]

## Impact

- **Severity:** [critical / high / medium / low]
- **Scope:** [tenant(s) affected, data classification]
- **User impact:** [if any]

## Root Cause Analysis

What caused the incident? (fill in after investigation)

## Remediation

What was done to resolve? (fill in after resolution)

## Prevention

What changes prevent recurrence? (e.g., new eval case in `evaluations/`, policy update, additional gate)

## Audit Trail

- **Audit log reference:** [if applicable]
- **Evidence hash:** [if applicable]

---

**Note:** This incident will be recorded in the audit log (C17) and may trigger a regression eval case in `evaluations/regression/` to prevent recurrence.
