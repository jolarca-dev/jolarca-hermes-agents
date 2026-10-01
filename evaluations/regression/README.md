# Regression Evaluations

**Status:** Deferred — intentionally empty; no incident history exists yet.
**Mandatory coverage:** no. C11 and C12 are already covered by the `privacy/` and
`prompt-injection/` suites, so this directory staying empty breaks no gate.

Regression evaluations pin an executable case for **every past agent incident** so
a failure once fixed can never silently return. They are the fleet's fail-closed
memory: hallucination, doctrinal or pastoral breach (C7), PII leak (C11),
injection bypass (C12), tenant-isolation failure (C2), unapproved publication (C3).

## Why this directory is empty today

The trigger is a real incident record and none exists. Verified 2026-10-01:
`gh issue list --state all` returns an empty set, so there are zero agent-incident
issues open **or** closed. The fleet has no runtime in production, so no observed
failure has yet been pinned.

## Trigger to populate

The incident source of record is the **Agent Incident** issue template,
`.github/ISSUE_TEMPLATE/agent_incident.md`. Populate a case when an issue filed
from that template is **closed** with both sections completed:

- **Root Cause Analysis**, and
- **Remediation**.

An incident that is open but not yet root-caused must **not** generate a case: the
expected outcome is still unknown, and pinning it early records a guess.

## Case-derivation rules

1. One closed incident yields at least one case; add more when it failed through
   several distinct paths.
2. Cases live in `regression/cases.yaml` with `suite: regression`, so incident
   coverage remains auditable as a distinct set.
3. Each case declares the `control` it guards and `maps_to` the real policy entry
   that failed, so grounding is enforced exactly as in the other suites.
4. Tag every derived case `incident:<issue-number>`, tracing it to the issue and
   through it to the immutable audit log and evidence hash (C17).
5. `expected_action` records the **required safe outcome** (block, deny, redact,
   escalate) — never what the fleet actually did at the time of the incident.
6. If the incident exposes a corpus-level gap rather than a single path, also add
   a sibling case to the matching behaviour suite (`prompt-injection/`, `privacy/`
   or `security/`).

## Acceptance criteria

A regression case is valid only when it is demonstrably **red-before / green-after**:
it would have failed against the pre-fix behaviour and passes against current policy.
Once a provider is registered, the same case must also pass against live model replay.

## Populating needs no CI change

`scripts/check_eval_coverage.py` and `tests/test_eval_cases.py` both discover
`evaluations/**/cases.yaml`, so a new case is grounding-checked by the
`adversarial-evals` job and schema-validated by the required `test` job. No
workflow edit is required.

## Contract

See `../README.md` for the case schema and the forbidden-token rule — reference
snake_case deny actions, never literal mission-platform resource strings.

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-10-01 | Expanded trigger to a closed, root-caused incident; added derivation rules and red-before/green-after acceptance criterion; recorded verified empty issue state | Agent (PR review) |
