# Threat Model — STRIDE Analysis

**Status:** Active
**Date:** 2026-10-01
**Compliance:** SOC 2 Type II (CC6.1–CC7.5), ISO 27001:2022 (A.5, A.8), GDPR Art. 32
**Scope:** 12-agent Hermes fleet (`jolarca-hermes-agents`)

---

## Overview

This threat model applies the STRIDE methodology to the Hermes agent fleet.
Each identified threat is mapped to the control(s) in `docs/control-matrix.md`
that mitigate it. A threat without a control is an unmitigated risk requiring
acceptance or remediation.

**Methodology:** For each STRIDE category, we identify threats specific to
the agent fleet's architecture (layered dependency graph, policy-as-code
enforcement, human gates at publication boundaries).

---

## Spoofing

*Threat: An attacker impersonates a legitimate entity to gain unauthorised access.*

| ID | Threat | Mitigation | Control | Severity |
|---|---|---|---|---|
| S1 | Attacker impersonates a tenant to access another tenant's data | Tenant-scoped index partitioning in `rag` agent; per-tenant access tokens | **C2** (tenant isolation) | High |
| S2 | Attacker forges an identity tag to bypass agent policy | Identity tag uniqueness enforced by CI (`validate_agents.py`); tags are never reused (HERMES-0001) | **C8** (deny patterns), HERMES-0001 | Medium |
| S3 | Attacker impersonates the orchestrator to issue unauthorised agent calls | Orchestrator is the sole entry point; agents only accept delegated calls from orchestrator; deny-pattern scan blocks unauthorised references | **C8**, **C9** | High |

---

## Tampering

*Threat: An attacker modifies data, configurations, or agent behaviour without authorisation.*

| ID | Threat | Mitigation | Control | Severity |
|---|---|---|---|---|
| T1 | Attacker modifies agent policy.yaml to weaken deny rules | All changes require PR through protected branch; CI `agent-policy-guard` validates policy structure; branch protection requires status checks | **C12** (injection defence), branch protection | High |
| T2 | Attacker injects false provenance citations into generated content | `editorial` agent verifies provenance completeness; missing or malformed citations cause automatic rejection | **C3** (editorial approval), **C4** (provenance) | High |
| T3 | Attacker modifies approved-source registry to include malicious sources | Source registry in `policies/approved_sources.md` requires PR review; `rag` agent validates against allow-list at retrieval time | **C1** (approved sources) | High |
| T4 | Attacker modifies translation output to introduce doctrinal errors | `translation` agent flags sensitive terms; `editorial` agent reviews all translated content before publication | **C5** (translation review), **C3** | Medium |
| T5 | Attacker tampers with audit logs to hide unauthorised actions | `audit` agent denies `modify_audit_log` and `delete_audit_log`; evidence hashing detects tampering; 7-year retention | **C17** (override audit), **C14** (retention) | Critical |

---

## Repudiation

*Threat: An attacker (or authorised user) performs an action and later denies it.*

| ID | Threat | Mitigation | Control | Severity |
|---|---|---|---|---|
| R1 | Operator publishes content and later denies authorship | Every publication carries editorial approval record with identity tag; 7-year retention of approval records | **C3** (editorial approval), **C14** | High |
| R2 | Operator modifies agent configuration and denies the change | All changes go through PR (git history); `audit` agent logs all human overrides with identity tag | **C17** (override audit) | High |
| R3 | Agent generates harmful content with no traceable source | Every claim must carry provenance citation (C4); provenance records include agent identity tag, source, and timestamp | **C4** (provenance) | Medium |
| R4 | Operator bypasses editorial gate and denies doing so | Editorial gate is enforced by policy deny rules; bypass attempt is logged by `audit` agent (C17) | **C3**, **C17** | High |

---

## Information Disclosure

*Threat: Sensitive data is exposed to unauthorised parties.*

| ID | Threat | Mitigation | Control | Severity |
|---|---|---|---|---|
| I1 | PII leaks into logs, telemetry, or public output | `consent` agent redacts PII before logging; `pii-scan` CI job validates no PII in agent policies; PII retention limited to 30 days | **C11** (PII redaction) | Critical |
| I2 | Tenant A's data is accessible to Tenant B | `rag` agent enforces tenant-scoped index access; cross-tenant access denied by policy | **C2** (tenant isolation) | Critical |
| I3 | Internal or confidential data appears in public output | Data classification flow requires editorial gate before publication; `website` agent verifies approval per artefact | **C3** (editorial approval), **C6** (accessibility) | High |
| I4 | LLM provider receives data beyond its DPIA scope | Model policy restricts data sent to provider; provider registry tracks approved scope; no provider currently approved | **C13** (vendor risk) | High |
| I5 | Conversation context leaks between Hermes and mission platform | Orchestrator isolates context; no shared memory; deny-pattern scan blocks cross-platform references | **C9** (no shared memory), **C10** (policy separation) | High |
| I6 | Prompt injection extracts confidential data from agent context | `guardrails` agent detects injection patterns; injection defence enforced by CI | **C12** (injection defence) | High |
| I7 | Approved source documents contain sensitive data not suitable for agent processing | Source approval criteria include data classification check (C1); sources classified above agent's level are rejected | **C1** (approved sources) | Medium |
| I8 | Special category data (religious beliefs) processed without safeguards | `guardrails` agent hard-escalates doctrinal content; no automated processing of Art. 9 data; `consent` agent redacts | **C7** (doctrine escalation), **C11** | Critical |

---

## Denial of Service

*Threat: An attacker or system failure prevents legitimate use of the agent fleet.*

| ID | Threat | Mitigation | Control | Severity |
|---|---|---|---|---|
| D1 | Runaway agent exhausts token budget | `orchestrator` enforces per-request (100k), per-day (1M tokens), and cost ($50/day) ceilings; `budget-check` CI validates limits exist | **C15** (budget) | High |
| D2 | LLM provider outage prevents all generation | Kill-switch circuit breaker in `orchestrator`; graceful degradation when provider unavailable; `kill-switch-test` CI validates circuit breaker exists | **C16** (kill-switch) | High |
| D3 | Prompt injection causes infinite loop or excessive API calls | `guardrails` agent detects and blocks injection; orchestrator enforces request-level budget ceiling | **C12**, **C15** | Medium |
| D4 | Accessibility gate stuck in failed state blocks all releases | Observability agent monitors gate health; alerting on prolonged gate failures; human override available | **C6** (accessibility), observability agent | Medium |

---

## Elevation of Privilege

*Threat: An attacker or agent gains capabilities beyond its authorised scope.*

| ID | Threat | Mitigation | Control | Severity |
|---|---|---|---|---|
| E1 | Agent writes directly to mission platform databases | Orchestrator policy denies mission DB writes; deny-pattern scan blocks mission-prefixed references across all agents | **C8** (no DB writes) | Critical |
| E2 | Agent bypasses editorial gate to publish without approval | Editorial gate enforced by policy deny rules; `website` agent verifies approval per artefact before composition | **C3** (editorial approval) | Critical |
| E3 | Lower-layer agent accesses higher-layer capabilities | Layered dependency graph enforces capability boundaries; agents can only delegate to agents in higher layers | HERMES-0001 (build order) | High |
| E4 | Agent accesses data from unapproved sources | `rag` agent allow-lists only approved sources; unapproved sources rejected at retrieval time | **C1** (approved sources) | High |
| E5 | Operator overrides safety controls without audit trail | All human overrides logged by `audit` agent with identity tag; 7-year retention of override records | **C17** (override audit) | High |
| E6 | Agent exceeds its data classification scope | Each agent declares `data_classification` in agent.yaml; CI validates classification matches agent role | **C2** (tenant isolation), agent-policy-guard | Medium |

---

## Control Coverage Matrix

| Control | Threats mitigated |
|---|---|
| C1 (approved sources) | T3, I7, E4 |
| C2 (tenant isolation) | S1, I2, E6 |
| C3 (editorial approval) | T2, R1, R4, I3, E2 |
| C4 (provenance) | T2, R3 |
| C5 (translation review) | T4 |
| C6 (accessibility) | I3, D4 |
| C7 (doctrine escalation) | I8 |
| C8 (no DB writes) | S2, S3, E1 |
| C9 (no shared memory) | S3, I5 |
| C10 (policy separation) | I5 |
| C11 (PII redaction) | I1, I8 |
| C12 (injection defence) | T1, I6, D3 |
| C13 (vendor risk) | I4 |
| C14 (retention) | R1, T5 |
| C15 (budget) | D1, D3 |
| C16 (kill-switch) | D2 |
| C17 (override audit) | R2, R4, T5, E5 |

**Coverage: 17/17 controls mitigate at least one identified threat.**
No control exists without a threat justification.

---

## Unmitigated Risks

| ID | Risk | Current State | Remediation | Owner |
|---|---|---|---|---|
| UR1 | Supply chain attack via compromised LLM provider | No provider selected; risk is theoretical until provider is onboarded | Model policy requires DPIA + security certification before any data is sent (C13) | orchestrator |
| UR2 | Zero-day vulnerability in agent framework dependencies | Dependabot configured; no runtime dependencies yet (agents are declarative YAML) | When runtime code is added, add dependency scanning to CI | observability |
| UR3 | Credential leak via agent misconfiguration | No credentials in agent configs; `.gitleaksignore` configured; gitleaks in pre-commit | Add secret scanning to CI when runtime code is added | guardrails |

---

## Assumptions and Limitations

1. **Verified:** The 17 controls in the control matrix are enforced by CI
   jobs that validate agent policy structure. The deny-pattern scanner
   confirms no forbidden references exist in the codebase.

2. **Assumed (not yet verified at runtime):** When agents gain runtime
   behaviour, the current declarative CI checks will need to be supplemented
   with runtime behavioural tests. The threat model assumes runtime
   enforcement will match the declarative policy — this must be verified
   when runtime code is written.

3. **Assumed:** Tenant isolation (C2) will be enforced at the index level
   when multi-tenant retrieval is implemented. Currently no retrieval
   runtime exists; the policy is declarative only.

4. **Limitation:** This threat model covers the agent fleet's internal
   architecture. External threats (network-level attacks, physical security,
   social engineering) are in scope for the broader jolarca-dev security
   posture but not modelled here.

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-10-01 | Initial STRIDE threat model (26 threats, 17 controls covered) | Agent (accepted by solo operator) |
