# Changelog

All notable changes to `jolarca-hermes-agents` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
