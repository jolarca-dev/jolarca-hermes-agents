# Control Matrix

**Status:** Accepted  
**Date:** 2026-09-30  
**Compliance:** SOC 2 Type II, ISO 27001:2022, GDPR Art. 32

---

## Overview

Every control below is mapped to three mandatory columns:

1. **Enforcement mechanism** — The automated check that fails when the control is violated
2. **Evidence location** — Where the proof of enforcement lands
3. **Failing CI job** — Which CI context fails when the control is breached

A control without an enforcement mechanism is folklore (ADR-0004 R3: "Enforced, not hoped for").

---

## Controls

| # | Control | Enforcement mechanism | Evidence location | Failing CI job |
|---|---|---|---|---|
| C1 | Approved-source retrieval only | `rag` agent policy denies unapproved sources; `scripts/check_approved_sources.py` validates source allow-list | `agents/rag/policy.yaml`, audit log | `agent-policy-guard` |
| C2 | Tenant and locale isolation | `rag` agent enforces tenant-scoped index access; `scripts/check_tenant_isolation.py` validates no cross-tenant queries | `agents/rag/policy.yaml`, audit log | `agent-policy-guard` |
| C3 | Editorial approval before publication | `editorial` agent requires human approver; `scripts/check_editorial_approval.py` validates approval record exists | `agents/editorial/policy.yaml`, approval log | `provenance-check` |
| C4 | Source provenance for every generated claim | `content` agent attaches source citations; `scripts/check_provenance.py` validates every claim has a citation | `agents/content/policy.yaml`, provenance log | `provenance-check` |
| C5 | Translation review for sensitive content | `translation` agent flags sensitive terms; `scripts/check_translation_review.py` validates review record | `agents/translation/policy.yaml`, review log | `agent-policy-guard` |
| C6 | Accessibility validation before release | `accessibility` agent runs WCAG checks; `scripts/check_accessibility.py` validates WCAG compliance | `agents/accessibility/policy.yaml`, validation report | `accessibility-gate` |
| C7 | No autonomous doctrinal or pastoral decisions | `guardrails` agent hard-escalates to human; `scripts/check_doctrine_escalation.py` validates escalation predicate | `agents/guardrails/policy.yaml`, escalation log | `agent-policy-guard` |
| C8 | No direct write access to mission databases | `orchestrator` agent policy denies mission DB writes; `scripts/check_deny_patterns.py` scans for mission-prefixed references | `agents/orchestrator/policy.yaml`, deny log | `deny-pattern-scan` |
| C9 | No shared conversational memory with JOL | `orchestrator` policy denies `cross_program_memory_access`; `scripts/check_deny_patterns.py` scans for mission-platform references | `agents/orchestrator/policy.yaml`, memory audit | `deny-pattern-scan` |
| C10 | Separate model and data-processing policies from JOL | `policies/` holds jolarca-specific policies; `scripts/check_deny_patterns.py` scans for mission-platform policy references | `policies/*.md`, policy audit | `deny-pattern-scan` |
| C11 | PII redaction before logging | `consent` agent redacts PII; `scripts/check_pii_redaction.py` validates policy; `scripts/check_eval_coverage.py` validates `evaluations/privacy/cases.yaml` | `agents/consent/policy.yaml`, `evaluations/privacy/cases.yaml`, redaction log | `pii-scan`, `adversarial-evals` |
| C12 | Prompt-injection defence | `guardrails` agent detects injection; `scripts/check_injection_defence.py` validates patterns; `scripts/check_eval_coverage.py` validates `evaluations/prompt-injection/cases.yaml` | `agents/guardrails/policy.yaml`, `evaluations/prompt-injection/cases.yaml`, injection log | `agent-policy-guard`, `adversarial-evals` |
| C13 | Model vendor risk assessment | `jolarca-vendor` repo holds vendor DPIA; `scripts/check_vendor_risk.py` validates all LLM providers are registered | `jolarca-vendor` (external), vendor register | `vendor-risk-check` |
| C14 | Output retention and deletion schedule | `audit` agent enforces retention policy; `scripts/check_retention.py` validates deletion schedule | `policies/retention.md`, retention log | `retention-check` |
| C15 | Cost/token budget ceilings | `orchestrator` agent enforces budget; `scripts/check_budget.py` validates token usage within ceiling | `agents/orchestrator/policy.yaml`, budget log | `budget-check` |
| C16 | Kill-switch and incident response | `orchestrator` agent implements circuit breaker; `scripts/check_kill_switch.py` validates kill-switch functional | `agents/orchestrator/policy.yaml`, incident log | `kill-switch-test` |
| C17 | Human-override audit trail | `audit` agent logs all human overrides; `scripts/check_override_audit.py` validates audit record exists | `agents/audit/policy.yaml`, override log | `audit-check` |

---

## Enforcement Layers

Controls are enforced at four layers:

1. **Agent policy layer** — Each agent's `policy.yaml` declares allow/deny rules. Enforced by `agent-policy-guard` CI job.
2. **Cross-agent validation layer** — Scripts that validate cross-agent contracts (e.g., provenance, editorial
   approval). Enforced by `provenance-check`, `accessibility-gate`.
3. **Fleet-wide deny-list layer** — Scripts that scan for forbidden patterns (e.g., mission-prefixed references,
   mission-platform access). Enforced by `deny-pattern-scan`.
4. **Adversarial evaluation layer** — Declarative attack/PII fixtures in `evaluations/`, grounded in agent policy and
   validated for coverage. Enforced by `adversarial-evals`.

---

## CI Job Mapping

| CI job | Controls enforced | Agent scope |
|---|---|---|
| `agent-policy-guard` | C1, C2, C5, C7, C12 | All agents |
| `provenance-check` | C3, C4 | content, editorial |
| `accessibility-gate` | C6 | accessibility |
| `deny-pattern-scan` | C8, C9, C10 | orchestrator, all agents |
| `pii-scan` | C11 | consent |
| `vendor-risk-check` | C13 | orchestrator (model selection) |
| `retention-check` | C14 | audit |
| `budget-check` | C15 | orchestrator |
| `kill-switch-test` | C16 | orchestrator |
| `audit-check` | C17 | audit |
| `adversarial-evals` | C11, C12 | consent, guardrails, orchestrator |

---

## Compliance Mapping

| Control | SOC 2 | ISO 27001 | GDPR |
|---|---|---|---|
| C1 (approved sources) | CC6.1, CC7.2 | A.5.1, A.8.1 | Art. 5(1)(b) |
| C2 (tenant isolation) | CC6.1, CC6.3 | A.8.13, A.5.15 | Art. 32 |
| C3 (editorial approval) | CC8.1 | A.8.32 | — |
| C4 (provenance) | CC7.2 | A.5.1 | Art. 5(1)(b) |
| C5 (translation review) | CC7.2 | A.5.1 | — |
| C6 (accessibility) | — | — | — (legal requirement) |
| C7 (doctrine escalation) | — | — | Art. 9 (special category) |
| C8 (no JOL DB writes) | CC6.1 | A.8.13 | Art. 5(1)(b) |
| C9 (no shared memory) | CC6.1 | A.8.13 | Art. 5(1)(b) |
| C10 (policy separation) | CC6.1 | A.5.1 | Art. 5(1)(b) |
| C11 (PII redaction) | CC6.1, CC7.2 | A.8.12 | Art. 32 |
| C12 (injection defence) | CC6.1, CC7.2 | A.8.8 | Art. 32 |
| C13 (vendor risk) | CC8.1 | A.5.19, A.5.20 | Art. 28 |
| C14 (retention) | CC7.2, CC8.1 | A.8.10 | Art. 5(1)(e), Art. 17 |
| C15 (budget) | — | — | — (operational) |
| C16 (kill-switch) | CC7.1, CC7.2 | A.5.24 | — |
| C17 (override audit) | CC8.1 | A.8.15 | — |

---

## Open Questions

### Resolved

1. **C6 (accessibility) — resolved 2026-09-30:** WCAG 2.1 AA is the target. Upgrade to 2.2 deferred.
2. **C7 (doctrine escalation) — resolved 2026-09-30:** Keyword-based detection. Patterns in `agents/guardrails/policy.yaml`.
3. **C13 (vendor risk) — resolved 2026-09-30:** Deferred to `jolarca-vendor` repo. No LLM provider selected yet.
4. **C15 (budget) — resolved 2026-09-30:** Orchestrator budget: 100k tokens/request, 1M tokens/day, $50/day ceiling.

### Deferred

None.

---

## Success Criteria

This control matrix is approved when:

- [x] All 17 controls have enforcement mechanisms defined
- [x] Every control maps to at least one failing CI job
- [x] Compliance mapping is reviewed by compliance authority
- [x] Open questions are resolved or deferred with recorded rationale

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-09-30 | Initial draft | Agent (pending review) |
| 2026-09-30 | All open questions resolved; success criteria met; status promoted to Accepted | Agent (accepted by solo operator) |
| 2026-10-01 | Added `adversarial-evals` job + `evaluations/` evidence for C11/C12; corrected C9/C10 to cite the existing `check_deny_patterns.py` (non-existent scripts removed) | Agent (proposed, PR review) |
