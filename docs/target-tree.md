# Target Directory Tree

**Status:** Accepted  
**Date:** 2026-09-30

---

## Overview

This is the target directory structure for `jolarca-hermes-agents`. It carries fleet-standard files (consistent with
sibling repos) plus agent-specific layout.

---

## Tree

```text
jolarca-hermes-agents/
│
├── .github/
│   ├── CODEOWNERS                          # * @JourneyOfLife (exists)
│   ├── dependabot.yml                      # Fleet convention
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── agent_incident.md               # Hallucination / doctrine breach
│   │   └── config.yml
│   └── workflows/
│       └── ci.yml                          # single workflow: 3 required jobs
│                                           # (lint, test, security) + supplementary
│                                           # control jobs incl. adversarial-evals
│
├── agents/
│   ├── orchestrator/                       # agent:jolarca:orchestrator (Layer 0)
│   │   ├── README.md                       # Purpose, boundaries, runbook
│   │   ├── agent.yaml                      # Identity tag, model policy, tool grants
│   │   ├── policy.yaml                     # Allow/deny actions, budget ceiling
│   │   ├── prompts/
│   │   │   └── system.md                   # System prompt
│   │   └── tests/
│   │       └── test_orchestrator.py
│   │
│   ├── guardrails/                         # agent:jolarca:guardrails (Layer 1)
│   │   ├── README.md
│   │   ├── agent.yaml
│   │   ├── policy.yaml                     # Deny-list, doctrine escalation predicate
│   │   ├── prompts/
│   │   │   └── system.md
│   │   └── tests/
│   │       └── test_guardrails.py
│   │
│   ├── rag/                                # agent:jolarca:rag (Layer 2)
│   │   ├── README.md
│   │   ├── agent.yaml
│   │   ├── policy.yaml                     # Approved-source allow-list, tenant isolation
│   │   ├── prompts/
│   │   │   └── system.md
│   │   └── tests/
│   │       └── test_rag.py
│   │
│   ├── consent/                            # agent:jolarca:consent (Layer 2)
│   │   ├── README.md
│   │   ├── agent.yaml
│   │   ├── policy.yaml                     # PII patterns, redaction rules
│   │   ├── prompts/
│   │   │   └── system.md
│   │   └── tests/
│   │       └── test_consent.py
│   │
│   ├── content/                            # agent:jolarca:content (Layer 3)
│   │   ├── README.md
│   │   ├── agent.yaml
│   │   ├── policy.yaml                     # Provenance attachment rules
│   │   ├── prompts/
│   │   │   └── system.md
│   │   └── tests/
│   │       └── test_content.py
│   │
│   ├── translation/                        # agent:jolarca:translation (Layer 4)
│   │   ├── README.md
│   │   ├── agent.yaml
│   │   ├── policy.yaml                     # Sensitive-term flagging
│   │   ├── prompts/
│   │   │   └── system.md
│   │   └── tests/
│   │       └── test_translation.py
│   │
│   ├── seo/                                # agent:jolarca:seo (Layer 4)
│   │   ├── README.md
│   │   ├── agent.yaml
│   │   ├── policy.yaml
│   │   ├── prompts/
│   │   │   └── system.md
│   │   └── tests/
│   │       └── test_seo.py
│   │
│   ├── accessibility/                      # agent:jolarca:accessibility (Layer 4)
│   │   ├── README.md
│   │   ├── agent.yaml
│   │   ├── policy.yaml                     # WCAG target (2.1 AA or 2.2)
│   │   ├── prompts/
│   │   │   └── system.md
│   │   └── tests/
│   │       └── test_accessibility.py
│   │
│   ├── editorial/                          # agent:jolarca:editorial (Layer 5)
│   │   ├── README.md
│   │   ├── agent.yaml
│   │   ├── policy.yaml                     # Approval workflow, provenance completeness
│   │   ├── prompts/
│   │   │   └── system.md
│   │   └── tests/
│   │       └── test_editorial.py
│   │
│   ├── website/                            # agent:jolarca:website (Layer 6)
│   │   ├── README.md
│   │   ├── agent.yaml
│   │   ├── policy.yaml
│   │   ├── prompts/
│   │   │   └── system.md
│   │   └── tests/
│   │       └── test_website.py
│   │
│   ├── audit/                              # agent:jolarca:audit (cross-cutting)
│   │   ├── README.md
│   │   ├── agent.yaml
│   │   ├── policy.yaml                     # Immutable logging, evidence hashing
│   │   ├── prompts/
│   │   │   └── system.md
│   │   └── tests/
│   │       └── test_audit.py
│   │
│   └── observability/                      # agent:jolarca:observability (cross-cutting)
│       ├── README.md
│       ├── agent.yaml
│       ├── policy.yaml                     # Telemetry scope, alerting rules
│       ├── prompts/
│       │   └── system.md
│       └── tests/
│           └── test_observability.py
│
├── schemas/
│   ├── agent.schema.json                   # JSON Schema for agent.yaml
│   ├── policy.schema.json                  # JSON Schema for policy.yaml
│   ├── provenance.schema.json              # JSON Schema for provenance records
│   └── eval-case.schema.json               # JSON Schema for evaluation cases
│
├── policies/
│   ├── model-policy.md                     # Model selection, vendor requirements
│   ├── data-processing-policy.md           # Data handling, classification rules
│   └── retention.md                        # Output retention and deletion schedule
│
├── docs/
│   ├── capability-map.md                   # 12-agent roster + build order (this phase)
│   ├── control-matrix.md                   # 17 controls → enforcement → evidence
│   ├── tool-register.md                    # Consolidated tool_grants -> control mapping
│   ├── architecture/
│   │   ├── context.mmd                     # C4 Level 1
│   │   ├── containers.mmd                  # C4 Level 2
│   │   └── trust-boundaries.mmd            # Data flow + trust boundaries
│   ├── adr/
│   │   ├── README.md
│   │   ├── TEMPLATE.md
│   │   ├── HERMES-0001-...                # First ADR
│   │   ├── HERMES-0002-...                 # Evaluations + tool register
│   │   └── HERMES-0003-...                 # Model sourcing + mission boundary
│   └── threat-model.md                     # STRIDE analysis
│
├── scripts/
│   ├── validate_agents.py                  # Schema validation for agent.yaml + policy.yaml
│   ├── check_deny_patterns.py              # C8, C9, C10: scan for mission-prefixed refs
│   ├── check_provenance.py                 # C4: validate source citations
│   ├── check_approved_sources.py           # C1: validate source allow-list
│   ├── check_tenant_isolation.py           # C2: validate tenant-scoped access
│   ├── check_editorial_approval.py         # C3: validate approval records
│   ├── check_translation_review.py         # C5: validate review records
│   ├── check_accessibility.py              # C6: WCAG validation
│   ├── check_doctrine_escalation.py        # C7: validate escalation predicate
│   ├── check_pii_redaction.py              # C11: PII scan
│   ├── check_injection_defence.py          # C12: injection pattern scan
│   ├── check_vendor_risk.py                # C13: vendor register check
│   ├── check_retention.py                  # C14: retention schedule check
│   ├── check_budget.py                     # C15: token budget check
│   ├── check_kill_switch.py                # C16: kill-switch functional test
│   ├── check_override_audit.py             # C17: override audit check
│   └── check_eval_coverage.py              # C11/C12: evaluation grounding + coverage
│
├── tests/
│   ├── conftest.py
│   ├── test_deny_patterns.py               # Fleet-wide deny-list tests
│   ├── test_schemas.py                     # JSON Schema validation tests
│   └── test_eval_cases.py                  # Eval-case schema conformance tests
│
├── evaluations/                            # Declarative eval fixtures (see evaluations/README.md)
│   ├── prompt-injection/cases.yaml         # C12 injection defence
│   ├── privacy/cases.yaml                  # C11 PII redaction / DSAR
│   ├── security/cases.yaml                 # C8, C9, C10 mission isolation
│   ├── functional/README.md                # Deferred: needs a runtime
│   └── regression/README.md                # Deferred: needs incident history
│
├── .editorconfig                           # Fleet convention
├── .gitattributes                          # Exists
├── .gitignore                              # Exists
├── .gitleaksignore                         # Fleet convention
├── .markdownlint.json                      # Fleet convention
├── .pre-commit-config.yaml                 # Fleet convention
├── CHANGELOG.md                            # Fleet convention
├── CONTRIBUTING.md                         # Fleet convention
├── LICENSE                                 # Exists (all-rights-reserved)
├── Makefile                                # Fleet convention
├── package.json                            # Dev-only: markdown lint tool (no runtime dependency)
├── package-lock.json                       # Integrity pin for markdownlint-cli2 + transitive deps
├── pyproject.toml                          # Fleet convention
├── qodana.yaml                             # Fleet convention
├── QODER.md                                # Fleet convention (agent behavioural contract)
├── README.md                               # Exists (needs update)
└── SECURITY.md                             # Exists
```

---

## Fleet-Standard Files

These files are present in every sibling repo. All of them now exist here; the
statuses below were reconciled against `git ls-files` on 2026-10-03.

| File | Status | Notes |
|---|---|---|
| `.editorconfig` | Present | Fleet convention |
| `.gitleaksignore` | Present | No ignore entries required |
| `.markdownlint.json` | Present | Enforced by the supplementary CI `markdown-lint` job (not a required context) |
| `.pre-commit-config.yaml` | Present | Hooks run per clone once `pre-commit install` has been executed; no CI job runs them. `trailing-whitespace` carries `--markdown-linebreak-ext=md` (see `tests/test_precommit_hook_safety.py`) |
| `CHANGELOG.md` | Present | Keep a Changelog format |
| `CONTRIBUTING.md` | Present | States the three repo invariants |
| `Makefile` | Present | Targets: help, lint, typecheck, test, validate, agents, schemas, deny-patterns, evals, markdown-lint, check |
| `pyproject.toml` | Present | Ruff, pytest and mypy config; no runtime dependencies |
| `qodana.yaml` | Present | Code quality config |
| `.github/dependabot.yml` | Present | github-actions, pip and npm ecosystems, weekly; manifest/ecosystem parity held by `tests/test_dependabot_coverage.py` |

---

## Agent File Conventions

Every agent directory follows the same structure:

| File | Purpose | Enforced by |
|---|---|---|
| `README.md` | Purpose, boundaries, runbook | Human review |
| `agent.yaml` | Identity tag, model policy, tool grants | `schemas/agent.schema.json` |
| `policy.yaml` | Allow/deny actions, specific rules | `schemas/policy.schema.json` |
| `prompts/system.md` | System prompt template | Human review |
| `tests/test_<agent>.py` | Agent-specific tests | CI `test` job |

---

## Build Order (from capability-map.md)

Files are created in dependency order:

1. **Schemas + policies** (no dependencies)
2. **Fleet-standard files** (no dependencies)
3. **orchestrator** (Layer 0)
4. **guardrails** (Layer 1)
5. **consent, rag** (Layer 2, parallel)
6. **content** (Layer 3)
7. **translation, seo, accessibility** (Layer 4, parallel)
8. **editorial** (Layer 5)
9. **website** (Layer 6)
10. **audit, observability** (cross-cutting, parallel with any layer)
11. **CI workflows** (after agents exist)
12. **Scripts** (after agents exist)

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-09-30 | Initial draft | Agent (pending review) |
| 2026-09-30 | Status promoted to Accepted (all agents scaffolded, all files present) | Agent (accepted by solo operator) |
| 2026-10-01 | Added `evaluations/`, `schemas/eval-case.schema.json`, `docs/tool-register.md`, `scripts/check_eval_coverage.py`, `tests/test_eval_cases.py`; corrected the workflows block to the single `ci.yml` job model | Agent (proposed, PR review) |
| 2026-10-01 | Added `HERMES-0003-...` to the ADR list | Agent (pending operator acceptance on merge) |
| 2026-10-03 | Added `QODER.md` to the root file list — it was introduced by PR #21 without reconciling this Accepted tree at the same time | Agent (proposed, PR review) |
| 2026-10-03 | Reconciled the Fleet-Standard Files table: all ten rows said `Missing` while all ten files were tracked and present, contradicting this document's own 2026-09-30 row ("all files present"). Statuses now read `Present`, and the two config-only files say so plainly rather than implying enforcement | Agent (proposed, PR review) |
| 2026-10-04 | Added `package.json` and `package-lock.json` to the root file list; `.markdownlint.json` status changed from config-only to enforced by the CI `markdown-lint` job | Agent (accepted, PR review) |
| 2026-10-04 | `.github/dependabot.yml` row updated: npm ecosystem registered for the root lockfile added with the markdownlint gate, parity held by `tests/test_dependabot_coverage.py` | Agent (accepted, PR review) |
| 2026-10-04 | Makefile row brought current -- 11 targets listed including the new `markdown-lint`, which is deliberately excluded from `check` | Agent (accepted, PR review) |
| 2026-10-04 | `.pre-commit-config.yaml` row corrected: it claimed the hooks were config-only and not installed, which described one working copy rather than the mechanism; now states per-clone installation, that no CI job runs them, and the markdown linebreak mitigation | Agent (accepted, PR review) |
