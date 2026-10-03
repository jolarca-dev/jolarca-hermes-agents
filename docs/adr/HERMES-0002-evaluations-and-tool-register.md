# HERMES-0002: Adversarial Evaluations and Consolidated Tool Register

**Status:** Proposed
**Date:** 2026-10-01
**Deciders:** jolarca-dev (solo operator)

---

## Context

`jolarca-hermes-agents` is a declarative, policy-as-code repository: 12 agents defined
by `agent.yaml` + `policy.yaml` + prompts, validated by `scripts/check_*.py` and CI.
A proposed restructure toward an executable `src/<project>_hermes/` runtime package was
reviewed and rejected because it would orphan the enforcement layer (`scripts/`), split
each agent across `src/` and `config/`, create two sources of truth for retention and
model policy, and drop compliance-critical documents (`control-matrix.md`,
`capability-map.md`, this ADR series). It also presumed a runtime and a model provider
that do not exist: `model_policy.provider` is `null` for all 12 agents and provider
selection is deferred to the `jolarca-vendor` DPIA (C13).

Two ideas from that proposal were genuinely valuable and are adopted here as *additions*
to the Accepted structure, not replacements:

1. A dedicated home for adversarial evaluations (`evaluations/`).
2. A consolidated tool register (`docs/tool-register.md`).

While verifying the current state, two drift defects were also confirmed and are fixed
here: `docs/control-matrix.md` C9 and C10 cited enforcement scripts
(`check_memory_isolation.py`, `check_policy_separation.py`) that do not exist — a direct
violation of ADR-0004 R3 ("a control without a failing CI job is folklore") — and
`docs/target-tree.md` listed per-control workflow files superseded by the single
`ci.yml`.

## Decision

### 1. `evaluations/` holds declarative fixtures, not a live harness

`evaluations/{prompt-injection,privacy,security}/cases.yaml` pin the attack and PII
corpus the fleet must withstand. `functional/` and `regression/` are documented
scaffolding with an explicit trigger to populate (a runtime, and an incident history,
respectively). No model provider exists, so a live harness has nothing to call; the
fixtures are written to be replayed unchanged once one is registered.

### 2. Grounding and coverage are enforced, not hoped for

- `schemas/eval-case.schema.json` defines the case contract; `tests/test_eval_cases.py`
  validates every suite against it in the required `test` job (jsonschema), so the schema
  is a source of truth rather than a decorative artifact.
- `scripts/check_eval_coverage.py` enforces (a) *grounding* — every `maps_to.entry` is a
  real entry in the referenced agent's `policy.yaml` — and (b) *coverage* — the suite
  collectively covers C11 and C12. It reads the actual policy vocabulary rather than
  hardcoding control wording. It runs in a new **supplementary** `adversarial-evals` CI
  job and via `make evals`.
- Fixtures must not embed literal mission-platform tokens; `check_deny_patterns.py` scans
  `evaluations/` and the fleet invariant (ADR-0004 R4) forbids those references. Cases
  reference the snake_case deny action instead.

### 3. `docs/tool-register.md` is a derived least-privilege register

It consolidates all 41 `tool_grants` (38 distinct) across the 12 agents, maps each tool
to its control, and records observations on the shared tools. The orchestrator
grant/policy mismatch surfaced during consolidation was fixed in a follow-up change and
is no longer an open observation. The `agent.yaml` files remain the source of truth; the
register never overrides them.

### 4. `adversarial-evals` is supplementary, not a required status check

Branch protection references exactly `lint`, `test`, `security`. The new job is added
alongside the other supplementary control jobs, so it does not alter the protected
contexts and requires no fleet allow-list change. `make evals` is deliberately kept out of
`make check` so the required `lint` gate is unchanged.

### 5. Correct the verified drift

`docs/control-matrix.md` C9/C10 now cite `scripts/check_deny_patterns.py` (which exists and
scans for mission-platform references covering both controls) instead of the non-existent
scripts. `docs/target-tree.md` now shows the single `ci.yml` job model and includes
`evaluations/`, `schemas/eval-case.schema.json`, and `docs/tool-register.md`.

## Consequences

### Positive

- C11 and C12 gain an executable, version-controlled adversarial corpus beyond static
  policy-config checks.
- Eval cases cannot drift from policy: grounding is machine-enforced.
- Tool grants are reviewable in one place for least-privilege and vendor-risk work.
- Two folklore controls (C9, C10) are re-anchored to real enforcement.

### Negative

- Fixtures are static until a provider exists; they do not yet exercise a live model.
- A second schema and CI job add maintenance surface.

### Risks

- Fixtures could embed a forbidden token and break the deny-pattern scan — mitigated by the
  forbidden-token rule in `evaluations/README.md` and by `check_deny_patterns.py` scanning
  the directory.
- The register could drift from `agent.yaml` — mitigated by declaring `agent.yaml` the
  source of truth, recording the register as derived, and re-deriving every figure it
  states on each test run in `tests/test_tool_register_consistency.py`. Declarative
  precedence alone proved insufficient: the totals sentence drifted to "39 distinct"
  against the 38 tools the register itself listed, and nothing failed.

---

## Compliance Mapping

| Aspect | SOC 2 | ISO 27001 | GDPR |
|---|---|---|---|
| Injection eval fixtures (C12) | CC6.1, CC7.2 | A.8.8 | Art. 32 |
| PII eval fixtures (C11) | CC6.1, CC7.2 | A.8.12 | Art. 32 |
| Tool register (least privilege) | CC6.1, CC6.2 | A.5.15, A.8.2 | Art. 5(1)(c) |
| Control-matrix drift fix (C9, C10) | CC7.2 | A.8.16 | Art. 5(1)(b) |

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-10-03 | Corrected §3: grants total 40 → 41 (the orchestrator gained `log_decision` after this ADR was drafted) and the now-resolved mismatch observation dropped from its description; §Risks mitigation upgraded from declarative precedence to the automated register-consistency guard | Agent (proposed, PR review) |
| 2026-10-01 | Initial ADR (proposed) | Agent (pending operator acceptance on merge) |
