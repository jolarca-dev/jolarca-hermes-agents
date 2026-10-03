# jolarca-hermes-agents

**Hermes AI agents for the `jolarca-dev` marketplace fleet.**

> **Compliance:** SOC 2 Type II (CC6.1-CC6.3, CC7.1-CC7.5) · ISO 27001:2022 (A.5, A.8) · GDPR (Art. 32)

---

## Purpose

This repository is the **authoritative source for Hermes AI agent implementations**
within the jolarca-dev marketplace fleet. It contains 12 agents organised in a
layered dependency graph, each with identity tags, policy files, system prompts,
and tests.

## Agent Fleet

```
Layer 0 ─── orchestrator ─── audit ─── observability
              │
Layer 1 ─── guardrails
              │
Layer 2 ─── consent ─── rag
                          │
Layer 3 ─── content ──────┘
              │
Layer 4 ─── translation ─ seo ─ accessibility
              │                        │
Layer 5 ─── editorial ─────────────────┘
              │
Layer 6 ─── website ─── (editorial + accessibility gates)
```

| Agent | Identity tag | Classification | Gate |
|---|---|---|---|
| orchestrator | `agent:jolarca:orchestrator` | internal | — |
| guardrails | `agent:jolarca:guardrails` | internal | blocks_all |
| consent | `agent:jolarca:consent` | restricted | blocks_all |
| rag | `agent:jolarca:rag` | confidential | — |
| content | `agent:jolarca:content` | confidential | editorial |
| translation | `agent:jolarca:translation` | confidential | editorial |
| seo | `agent:jolarca:seo` | public | editorial |
| accessibility | `agent:jolarca:accessibility` | public | blocks_release |
| editorial | `agent:jolarca:editorial` | confidential | human_approver |
| audit | `agent:jolarca:audit` | confidential | — |
| observability | `agent:jolarca:observability` | internal | — |
| website | `agent:jolarca:website` | public | editorial |

## Repository Structure

```
jolarca-hermes-agents/
├── agents/
│   ├── orchestrator/          # Layer 0: routing, budget, kill-switch
│   ├── guardrails/            # Layer 1: injection defence, deny-list
│   ├── consent/               # Layer 2: PII redaction, DSAR
│   ├── rag/                   # Layer 2: approved-source retrieval
│   ├── content/               # Layer 3: draft generation
│   ├── translation/           # Layer 4: locale rendering
│   ├── seo/                   # Layer 4: metadata, structured data
│   ├── accessibility/         # Layer 4: WCAG validation
│   ├── editorial/             # Layer 5: approval workflow
│   ├── audit/                 # Cross-cutting: immutable logging
│   ├── observability/         # Cross-cutting: telemetry, drift
│   └── website/               # Layer 6: site composition
├── schemas/                   # JSON Schemas (agent, policy, provenance, eval-case)
├── policies/                  # approved_sources, retention, terminology
├── scripts/                   # Validation + control-enforcement scripts
├── tests/                     # Cross-agent + schema-conformance tests
├── evaluations/               # Adversarial/PII fixtures (C11, C12, C8-C10)
├── docs/
│   ├── capability-map.md      # 12-agent roster + build order
│   ├── control-matrix.md      # 17 controls -> enforcement -> evidence
│   ├── tool-register.md       # Consolidated tool_grants -> control mapping
│   ├── target-tree.md         # Directory structure spec
│   └── adr/
│       ├── HERMES-0001-*.md   # Architecture decisions
│       └── HERMES-0002-*.md   # Evaluations + tool register
├── .github/workflows/ci.yml   # CI: lint, test, security + 11 control jobs
├── Makefile                   # lint, test, validate, check
├── pyproject.toml             # Python project config
└── CHANGELOG.md               # Change log
```

## Commands

```bash
make check       # Full pre-merge check (lint + validate + deny-patterns)
make lint        # Ruff linter
make test        # Run all tests
make validate    # Validate agent schemas + JSON schemas
make evals       # Validate evaluation suite grounding + coverage
make deny-patterns  # Scan for forbidden mission-platform references
```

## CI Pipeline

**Required checks** (branch protection): `lint`, `test`, `security`

**Supplementary control jobs:** `agent-policy-guard`, `provenance-check`,
`deny-pattern-scan`, `vendor-risk-check`, `pii-scan`, `retention-check`,
`budget-check`, `kill-switch-test`, `audit-check`, `accessibility-gate`,
`adversarial-evals`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

See [LICENSE](./LICENSE). Copyright (c) 2026 jolarca-dev. All rights reserved.
