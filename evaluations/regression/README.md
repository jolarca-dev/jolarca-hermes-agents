# Regression Evaluations

**Status:** Deferred — not yet populated.

Regression evaluations pin a case for every past incident (hallucination,
doctrine breach, PII leak, injection success) so a fixed failure can never
silently return. They require an **incident history**, and none is recorded yet:
the fleet has no runtime in production.

## Trigger to populate

Create `regression/cases.yaml` from the first filed agent-incident report. Each
closed incident becomes at least one regression case referencing the incident id
in `tags`, so the case is traceable back to the audit log (C17).

## Contract

Follow `schemas/eval-case.schema.json` (see `../README.md`). A regression case
reuses the suite of the behaviour it guards (injection, privacy, security) and
adds an `incident:<id>` tag for traceability.
