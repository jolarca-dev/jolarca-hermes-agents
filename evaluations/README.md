# Evaluations

Declarative evaluation suites for the Hermes agent fleet.

**Status:** structure Accepted; cases are static fixtures
**Compliance:** strengthens C11 (PII redaction) and C12 (prompt-injection defence);
`security/` adds behavioural coverage for C8/C9/C10.

---

## Why static fixtures

No LLM provider is registered yet: `model_policy.provider` is `null` across all
12 agents and provider selection is deferred to the `jolarca-vendor` DPIA (C13).
A live adversarial harness therefore has nothing to call. These suites are
version-controlled **case fixtures** that:

1. pin the attack/PII corpus the fleet must withstand, and
2. are validated today for *policy grounding* and *control coverage*.

When a provider is registered, a live runner replays these same fixtures against
the model and diffs actual behaviour against each case's `expected_action`.

## Layout

| Suite | Control | Grounded in |
|---|---|---|
| `prompt-injection/cases.yaml` | C12 | `agents/guardrails/policy.yaml` escalation patterns |
| `privacy/cases.yaml` | C11 | `agents/consent/policy.yaml` allow/deny/escalation entries |
| `security/cases.yaml` | C8, C9, C10 | `agents/orchestrator/policy.yaml` deny actions |
| `functional/` | deferred | needs a runtime (none exists yet) |
| `regression/` | deferred | needs incident history (none recorded yet) |

## Case contract

Each `cases.yaml` validates against `schemas/eval-case.schema.json`:

- `suite` — suite identifier (matches the directory name)
- `control` — primary control-matrix control the suite strengthens
- `cases[]` — each case requires `id`, `input`, `expected_action`,
  `maps_to {agent, entry, kind}`, and `control`

`maps_to.entry` **must** be a real entry in the referenced agent's `policy.yaml`
(escalation pattern, deny action, or allow action). This is enforced by
`scripts/check_eval_coverage.py`, so a case can never drift from the policy it
claims to exercise.

## Forbidden-token rule

Case inputs must **not** embed literal mission-platform tokens (the resource
strings denied in each `policy.yaml` under `deny.resources`).
`scripts/check_deny_patterns.py` scans this directory and would fail the build.
Reference those resources by the snake_case deny **action** instead (for example
`mission_platform_access`).

## Running

```bash
make evals                       # grounding + control-coverage check
pytest tests/test_eval_cases.py  # schema conformance
```

CI enforces both: the `adversarial-evals` supplementary job runs
`check_eval_coverage.py`, and the required `test` job runs the schema tests.
