# Functional Evaluations

**Status:** Deferred — intentionally empty, not yet populated.
**Mandatory coverage:** no. `scripts/check_eval_coverage.py` requires only C11 and
C12 across the suite set, so this directory staying empty does not weaken any gate.

Functional evaluations assert that a **benign** request produces the intended
end-to-end behaviour: routing and delegation (`orchestrator`), approved-source
retrieval (`rag`), drafting with provenance (`content`), locale rendering
(`translation`), and composition behind the editorial and accessibility gates
(`website`).

## Why this directory is empty today

A functional case is only worth having if it can be executed. Two prerequisites do
not exist yet, and each is verifiable rather than assumed:

1. **No agent runtime.** This repository holds declarative agent definitions
   (`agent.yaml`, `policy.yaml`, prompts). There is no code path that loads a
   definition and completes a request.
2. **No model provider.** `model_policy.provider` is `null` for all 12 agents;
   provider selection is deferred to the `jolarca-vendor` DPIA (C13).

Shipping a `cases.yaml` now would create an artifact nothing can run — folklore
under ADR-0004 R3. The enforced suites are `prompt-injection/`, `privacy/` and
`security/`.

## Preconditions to populate (all three must hold)

- [ ] A runtime can load an `agents/<name>/` definition and complete one request.
- [ ] `model_policy.provider` is non-null for the agent under test, and that
      provider is registered in `jolarca-vendor` with a completed DPIA (C13).
- [ ] A deterministic oracle exists for the expected outcome — an approval record,
      a composed artefact, or a routing decision a case can assert against.

## Acceptance criteria for the first `functional/cases.yaml`

1. Validates against `schemas/eval-case.schema.json`.
2. Every case declares `control` — the schema makes it **required** (pattern
   `^C[0-9]+$`). Use the control the behaviour realises: `C1` for approved-source
   retrieval, `C3` for the editorial gate, `C4` for provenance, `C15` for
   delegation within budget.
3. Every `maps_to.entry` exists in the named agent's `policy.yaml`; functional
   expectations use `kind: allow_action`.
4. `expected_action: allow` for benign paths. A functional case fails when the
   fleet blocks work it should have permitted — the inverse of the adversarial
   suites.
5. Green under both `make evals` and `pytest tests/test_eval_cases.py`.

## Populating needs no CI change

Both existing gates discover new suites automatically:

- `scripts/check_eval_coverage.py` walks `evaluations/**/cases.yaml`, so a new file
  is grounding-checked by the `adversarial-evals` job.
- `tests/test_eval_cases.py` parametrises over the same glob, so the new file is
  schema-validated by the required `test` job.

## Non-goals

Do not restate structural or policy checks here. Those need no runtime and are
already enforced by `scripts/check_*.py`; duplicating them would create two
sources of truth for one control.

## Contract

See `../README.md` for the case schema and the forbidden-token rule: inputs must
not embed literal mission-platform resource strings, because
`scripts/check_deny_patterns.py` scans this directory. Reference the snake_case
deny **action** instead.

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-10-01 | Expanded populate preconditions and acceptance criteria; corrected `control` from optional to required per the schema | Agent (PR review) |
