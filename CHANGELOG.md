# Changelog

All notable changes to `jolarca-hermes-agents` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed — 2026-10-03

- `.github/workflows/ci.yml`: removed the shell OR-true from the `security` job's `bandit`
  scan, so that **required status check can now fail**. It previously ended
  `bandit -r . -x .venv/ -ll || true`, discarding the scan's exit status: the job reported
  green whether or not bandit found anything. Because `security` is one of the three
  branch-protection required contexts, that green is read as assurance both by the merge
  gate and by an auditor. This is the mirror image of ADR-0004 R3's "a control without a
  failing CI job is folklore" — a job that cannot fail manufactures assurance.
  Verified safe to enable: bandit over the repository's own Python (1,698 LOC, which is
  the scope CI sees, since its checkout contains no virtual environment) exits 0 with
  0 High and 0 Medium at the `-ll` threshold; the 152 Low findings stay below it.
  `-x .venv/` is left untouched — it is inert in CI, and narrowing scan scope is a
  separate concern from making the gate binding.
- `tests/test_ci_gates_are_real.py`: regression guard for both ways a GitHub Actions gate
  gets neutered — an exit-status swallow such as OR-true, and `continue-on-error` on a
  step or a job — plus a check that the `security` context still invokes a real bandit
  scan and a non-vacuity test so a workflow-format change cannot turn these assertions
  into trivial passes. Written before the fix and observed failing on `ci.yml:security`.

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
