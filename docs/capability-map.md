# Agent Capability Map

**Status:** Draft — pending review  
**Date:** 2026-09-30  
**ADR prefix:** HERMES-

---

## Overview

This document defines the 12-agent capability map for `jolarca-hermes-agents`. Each agent is an independently testable module with a unique identity tag, responsibility boundary, and dependency graph.

The capability map is the foundation for all subsequent work: directory structure, policy files, control matrix, and CI enforcement. **No agent scaffold begins until this map is approved.**

---

## Capability Table

| Module id | Identity tag | Responsibility | Depends on | Data classification | Human gate |
|---|---|---|---|---|---|
| `orchestrator` | `agent:jolarca:orchestrator` | Routing, delegation, budget/cost caps, kill-switch | — | internal | — |
| `guardrails` | `agent:jolarca:guardrails` | Prompt-injection defence, deny-list enforcement, doctrine/pastoral escalation | orchestrator | internal | blocks all |
| `rag` | `agent:jolarca:rag` | Approved-source retrieval, tenant/locale-scoped index access | guardrails | confidential | — |
| `content` | `agent:jolarca:content` | Draft generation from retrieved sources only | rag, guardrails | confidential | editorial |
| `translation` | `agent:jolarca:translation` | Locale rendering, terminology consistency | content | confidential | editorial (sensitive) |
| `seo` | `agent:jolarca:seo` | Metadata, structured data, keyword fitness | content | public | editorial |
| `accessibility` | `agent:jolarca:accessibility` | WCAG validation, release gate | content | public | blocks release |
| `editorial` | `agent:jolarca:editorial` | Approval workflow, provenance completeness check | content, translation | confidential | human approver |
| `consent` | `agent:jolarca:consent` | PII detection/redaction, DSAR support, purpose-limitation checks | guardrails | restricted | blocks all |
| `audit` | `agent:jolarca:audit` | Immutable decision logging, evidence hashing, drift detection | all | confidential | — |
| `observability` | `agent:jolarca:observability` | Model/eval drift, token+cost telemetry, incident signals | all | internal | — |
| `website` | `agent:jolarca:website` | Site composition from approved, gated artefacts | editorial, accessibility | public | editorial |

---

## Build Order

Dependencies flow downward. An agent must not be built before its dependencies exist.

```
Layer 0 (foundation):
  orchestrator

Layer 1 (safety boundary):
  guardrails ← orchestrator

Layer 2 (data access + compliance):
  consent ← guardrails
  rag ← guardrails

Layer 3 (generation):
  content ← rag, guardrails

Layer 4 (specialization):
  translation ← content
  seo ← content
  accessibility ← content

Layer 5 (approval):
  editorial ← content, translation

Layer 6 (composition):
  website ← editorial, accessibility

Cross-cutting (span all layers, ship alongside orchestrator):
  audit
  observability
```

**Parallelizable within layers:**
- Layer 2: `consent` and `rag` can be built in parallel
- Layer 4: `translation`, `seo`, `accessibility` can be built in parallel
- Cross-cutting: `audit` and `observability` can be built alongside any layer

---

## Identity Tag Namespace

All identity tags follow the pattern `agent:jolarca:<module-id>`.

**Rules:**
1. Tags are lowercase, hyphen-separated, matching the module id
2. Tags are never reused or reassigned (consistent with ADR prefix rules)
3. Every agent must declare its tag in `agent.yaml`; policy enforcement rejects untagged agents
4. Tags are used in audit logs, policy files, and CI enforcement

**Allocated tags:**
- `agent:jolarca:orchestrator`
- `agent:jolarca:guardrails`
- `agent:jolarca:rag`
- `agent:jolarca:content`
- `agent:jolarca:translation`
- `agent:jolarca:seo`
- `agent:jolarca:accessibility`
- `agent:jolarca:editorial`
- `agent:jolarca:consent`
- `agent:jolarca:audit`
- `agent:jolarca:observability`
- `agent:jolarca:website`

---

## Data Classification Rationale

| Classification | Agents | Rationale |
|---|---|---|
| `internal` | orchestrator, guardrails, observability | Code/config only; no production data at rest |
| `confidential` | rag, content, translation, editorial, audit | Processes marketplace content; may touch user-generated content but not PII at rest |
| `restricted` | consent | Handles PII detection/redaction; must not log or retain PII |
| `public` | seo, accessibility, website | Output is public-facing; no sensitive data in transit or at rest |

**GDPR Art. 9 trigger:** If any agent processes religious-context data (e.g., liturgical content, pastoral references), the classification must be elevated to `restricted` and a DPIA triggered. This is a scheduled re-evaluation point, not a current gap.

---

## Human Gates

Three types of human gates are defined:

1. **blocks all** — The agent cannot proceed without human approval. Example: `guardrails` escalates doctrinal/pastoral questions to a human; no autonomous decision permitted.
2. **editorial** — The agent's output requires human editorial approval before publication. Example: `content` drafts must be approved by `editorial`.
3. **blocks release** — The agent's validation must pass before release. Example: `accessibility` WCAG checks must pass before deployment.

**Solo-era deviation (D-04 equivalent):** In the solo-operator era, "human approval" means the operator reviews and merges the PR. When teams are created, these gates map to team-based approval workflows.

---

## Open Questions

1. **Doctrinal escalation predicate:** What specific content patterns trigger the `guardrails` doctrinal escalation? This needs a defined detection predicate (e.g., keywords, semantic similarity to catechism texts).
2. **Tenant isolation model:** How is tenant data isolated in `rag`? Per-tenant index? Row-level security? This affects the `confidential` classification enforcement.
3. **Model vendor DPIA:** Which LLM providers are in scope? Are they registered in `jolarca-vendor` with completed risk scoring?
4. **Kill-switch mechanism:** How does `orchestrator` implement the kill-switch? Circuit breaker? Manual override? This needs a defined failure mode.

---

## Success Criteria

This capability map is approved when:

- [ ] All 12 module ids are confirmed (no additions, no deletions)
- [ ] Build order is accepted (dependencies are correct)
- [ ] Data classifications are reviewed and accepted
- [ ] Human gates are mapped to actual approval workflows
- [ ] Open questions are resolved or deferred with recorded rationale

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-09-30 | Initial draft | Agent (pending review) |
