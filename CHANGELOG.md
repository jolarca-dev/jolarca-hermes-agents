# Changelog

All notable changes to `jolarca-hermes-agents` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
