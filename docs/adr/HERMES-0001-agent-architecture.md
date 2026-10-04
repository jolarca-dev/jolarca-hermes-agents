# HERMES-0001: Agent Architecture — Identity Tags, Build Order, and Gate Types

**Status:** Accepted
**Date:** 2026-09-30
**Deciders:** jolarca-dev (solo operator)

---

## Context

The `jolarca-hermes-agents` repository implements 12 AI agents for the jolarca-dev
marketplace fleet. Each agent operates under SOC 2 Type II, ISO 27001:2022, and
GDPR controls. The architecture needed to answer:

1. How are agents uniquely identified across the fleet?
2. In what order must agents be built (dependency graph)?
3. What types of human gates exist and when do they apply?

## Decision

### 1. Identity Tag Namespace

Every agent declares a unique identity tag in `agent.yaml` following the pattern:

```text
agent:jolarca:<module-id>
```

**Rules:**

- Tags are lowercase, hyphen-separated, matching the module id
- Tags are never reused or reassigned
- Every agent must declare its tag; untagged agents are rejected by CI
- Tags are used in audit logs, policy files, and CI enforcement

**Allocated tags:**

| Module id | Identity tag |
| --- | --- |
| orchestrator | `agent:jolarca:orchestrator` |
| guardrails | `agent:jolarca:guardrails` |
| consent | `agent:jolarca:consent` |
| rag | `agent:jolarca:rag` |
| content | `agent:jolarca:content` |
| translation | `agent:jolarca:translation` |
| seo | `agent:jolarca:seo` |
| accessibility | `agent:jolarca:accessibility` |
| editorial | `agent:jolarca:editorial` |
| audit | `agent:jolarca:audit` |
| observability | `agent:jolarca:observability` |
| website | `agent:jolarca:website` |

### 2. Build Order (Layered Dependency Graph)

Agents are built in dependency order. An agent must not be built before its
dependencies exist.

```text
Layer 0 (foundation):
  orchestrator, audit (cross-cutting), observability (cross-cutting)

Layer 1 (safety boundary):
  guardrails <- orchestrator

Layer 2 (data access + compliance):
  consent <- guardrails
  rag <- guardrails

Layer 3 (generation):
  content <- rag, guardrails

Layer 4 (specialization):
  translation <- content
  seo <- content
  accessibility <- content

Layer 5 (approval):
  editorial <- content, translation

Layer 6 (composition):
  website <- editorial, accessibility
```

Parallelizable within layers:

- Layer 2: consent and rag
- Layer 4: translation, seo, accessibility

### 3. Human Gate Types

Three types of human gates are defined:

| Gate type | Meaning | Example |
| --- | --- | --- |
| `blocks_all` | Agent cannot proceed without human approval | guardrails (doctrinal escalation) |
| `editorial` | Output requires human editorial approval before publication | content, translation, seo |
| `blocks_release` | Agent's validation must pass before release | accessibility (WCAG gate) |
| `human_approver` | A human must explicitly approve/reject | editorial (approval workflow) |
| `none` | No human gate; automated | orchestrator, rag, audit, observability |

**Solo-era deviation (D-04 equivalent):** In the solo-operator era, "human
approval" means the operator reviews and merges the PR. When teams are created,
these gates map to team-based approval workflows.

## Consequences

### Positive

- Unique identity tags enable fleet-wide audit correlation
- Layered build order prevents circular dependencies
- Gate types provide clear compliance semantics

### Negative

- Identity tags add YAML boilerplate to every agent
- Layered build order means early layers must be stable before later layers begin

### Risks

- Tag reuse could cause audit log confusion — mitigated by uniqueness enforcement in CI
- Gate bypass could violate compliance — mitigated by policy deny rules and CI checks

---

## Compliance Mapping

| Control | SOC 2 | ISO 27001 | GDPR |
| --- | --- | --- | --- |
| Identity tags | CC7.2 (audit trail) | A.8.32 (audit logging) | Art. 30 (records) |
| Build order | CC6.1 (access control) | A.8.13 (info transfer) | Art. 5(1)(b) |
| Human gates | CC8.1 (change mgmt) | A.8.32 (audit logging) | Art. 9 (special category) |

---

## Revision History

| Date | Change | Authority |
| --- | --- | --- |
| 2026-09-30 | Initial ADR | Agent (accepted by solo operator) |
