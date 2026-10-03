# Changelog

All notable changes to `jolarca-hermes-agents` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added — 2026-10-03

- `.github/workflows/ci.yml`: wired the eight `scripts/check_*.py` enforcement scripts that
  existed and passed standalone but were invoked by no CI job, which left C1, C2, C3, C4,
  C5, C7, C12 and C13 folklore under ADR-0004 R3 ("a control without a failing CI job is
  folklore"). Two supplementary jobs were created — `provenance-check` (C3 editorial
  approval, C4 source provenance) and `vendor-risk-check` (C13 model vendor risk and the
  null-provider invariant) — making the job names `docs/control-matrix.md` already cited
  real, and five control steps were added to `agent-policy-guard` (C1 approved sources,
  C2 tenant isolation, C5 translation review, C7 doctrine escalation, C12 injection
  defence) to match the coverage that matrix already attributed to it. Job count 12 → 14.
  The three required status checks (`lint`, `test`, `security`) are unchanged, so neither
  branch protection nor the fleet allow-list needs updating.
- `tests/test_ci_control_wiring.py`: regression guard for both drift classes — every
  `scripts/check_*.py` must be invoked by a CI job, and every job the control matrix cites
  must be defined in `ci.yml`. Includes a non-vacuity test so a parser that silently
  matches nothing cannot turn those assertions into trivial passes, and a check that the
  protected status contexts keep their exact names.

### Changed — 2026-10-03

- `docs/adr/HERMES-0003-model-sourcing-and-mission-boundary.md` §4: now names
  `vendor-risk-check` as the enforcement locus for the null-provider invariant. The prior
  wording said only that `check_vendor_risk.py` "keeps asserting" it; because no job
  invoked that script, the assertion was not enforced. Revision History records the
  correction rather than silently rewriting the claim.
- `README.md`: supplementary control job list and the `ci.yml` structure comment updated
  from 9 jobs to 11.

### Added — 2026-10-01

- `docs/adr/HERMES-0003-model-sourcing-and-mission-boundary.md`: records that self-hosted
  inference for the Baltic (LT/LV/EE) pilot is a mission-side concern; this marketplace
  fleet must not couple to a mission inference resource (ADR-0004 R4, enforced by
  `check_deny_patterns.py`); two compliant sourcing paths are defined — a marketplace-owned
  self-hosted endpoint (assessed as infrastructure risk + model provenance, not a third-party
  DPIA) or a registered third-party provider via the full C13 DPIA. Providers stay `null`; no
  mission token is introduced.

### Changed — 2026-10-01

- `docs/adr/README.md`: added the HERMES-0003 row and restored the missing HERMES-0002 index
  entry; `docs/target-tree.md` ADR list extended to HERMES-0003

### Changed — 2026-10-01

- `evaluations/functional/README.md` and `evaluations/regression/README.md`: explicit
  populate preconditions, derivation rules, acceptance criteria, and the fact that
  populating needs no CI change (both gates discover `evaluations/**/cases.yaml`)
- `docs/tool-register.md`: both remaining observations reviewed against `policy.yaml`
  evidence and confirmed correct by design; opened one runtime follow-up on the shared
  `drift_detected` escalation pattern name declared by both audit and observability

### Fixed — 2026-10-01

- `evaluations/functional/README.md` contradicted `schemas/eval-case.schema.json` by
  describing `control` as optional; the schema requires it on every case

### Added — 2026-10-01

- `evaluations/` declarative adversarial suite: `prompt-injection` (C12), `privacy` (C11),
  `security` (C8/C9/C10) fixtures, plus `functional`/`regression` scaffolding
- `schemas/eval-case.schema.json` and `scripts/check_eval_coverage.py`
  (policy grounding + control coverage); `tests/test_eval_cases.py` (schema conformance)
- `docs/tool-register.md`: consolidated `tool_grants` -> control mapping across all 12 agents
- `docs/adr/HERMES-0002-evaluations-and-tool-register.md`
- `adversarial-evals` supplementary CI job and `make evals` target

### Fixed — 2026-10-01

- `docs/control-matrix.md`: C9/C10 no longer cite non-existent scripts
  (`check_memory_isolation.py`, `check_policy_separation.py`); enforcement repointed to
  the existing `check_deny_patterns.py`
- `docs/target-tree.md`: replaced fictional per-control workflow files with the single
  `ci.yml` job model

### Added — 2026-09-30

- Fleet-standard files: `.editorconfig`, `.markdownlint.json`, `.pre-commit-config.yaml`,
  `.gitleaksignore`, `qodana.yaml`, `.github/dependabot.yml`, `Makefile`, `pyproject.toml`
- Capability map: 12-agent roster with identity tags, dependencies, build order
- Control matrix: 17 controls mapped to enforcement mechanisms and CI jobs
- Target tree: full directory structure with agent file conventions
- Orchestrator agent scaffold (Layer 0)
- Guardrails agent scaffold (Layer 1)
- JSON Schemas for `agent.yaml` and `policy.yaml`
- Validation scripts: `validate_agents.py`, `check_deny_patterns.py`
- CI workflow with lint, test, security checks

### Governance — 2026-09-30

- Registered in fleet allow-list (`jolarca-control/repos/jolarca-hermes-agents.yml`)
- ADR prefix `HERMES-` allocated in `jolarca-docs/adr/namespace.md`
- Terraform state reconciliation complete (import + branch protection applied)
- LICENSE aligned to fleet convention (all-rights-reserved)

## [0.0.0] — 2026-09-30

- Initial repository scaffold (README, SECURITY, LICENSE, CODEOWNERS, CI)
