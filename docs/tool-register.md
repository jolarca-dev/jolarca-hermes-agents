# Tool Register

**Status:** Accepted
**Date:** 2026-10-01
**Source of truth:** each agent's `agent.yaml` `tool_grants` (this document is a *derived* register)

---

## Purpose

Every tool grant in the fleet lives inside an individual `agent.yaml`. This register
consolidates them into one least-privilege view so a reviewer can answer, without
opening twelve files: *which agent holds which tool, what control does that tool
serve, and is any grant duplicated or inconsistent?*

If this register and an `agent.yaml` disagree, the `agent.yaml` wins — update this
document, never the reverse.

## Grants by agent

| Agent | Classification | Gate | `tool_grants` |
|---|---|---|---|
| orchestrator | internal | none | `delegate_to_agent`, `check_budget`, `kill_switch`, `log_decision` |
| guardrails | internal | blocks_all | `inspect_input`, `inspect_output`, `block_request`, `escalate_to_human` |
| consent | restricted | blocks_all | `detect_pii`, `redact_pii`, `log_redaction`, `support_dsar` |
| rag | confidential | none | `query_index`, `retrieve_documents`, `check_source_approval` |
| content | confidential | editorial | `generate_draft`, `attach_provenance`, `request_editorial_approval` |
| translation | confidential | editorial | `translate_content`, `check_terminology`, `request_editorial_approval` |
| seo | public | editorial | `generate_metadata`, `generate_structured_data`, `check_keyword_fitness` |
| accessibility | public | blocks_release | `validate_wcag`, `check_alt_text`, `check_color_contrast`, `block_release` |
| editorial | confidential | human_approver | `approve_content`, `reject_content`, `check_provenance_completeness`, `log_approval` |
| audit | confidential | none | `log_decision`, `hash_evidence`, `detect_drift` |
| observability | internal | none | `collect_telemetry`, `detect_drift`, `emit_incident_signal` |
| website | public | editorial | `compose_page`, `check_editorial_approval`, `check_accessibility_gate` |

**Totals (verified):** 41 grants across 12 agents; 38 distinct tools. Three tools are
shared: `detect_drift` (audit, observability), `request_editorial_approval`
(content, translation), and `log_decision` (orchestrator, audit).

## Tool index → control mapping

| Tool | Held by | Control | Purpose |
|---|---|---|---|
| `delegate_to_agent` | orchestrator | C15 | Route work to a lower-layer agent within budget |
| `check_budget` | orchestrator | C15 | Enforce token/cost ceilings |
| `kill_switch` | orchestrator | C16 | Circuit breaker; halts all agent operations |
| `inspect_input` | guardrails | C12 | Scan inbound prompts for injection |
| `inspect_output` | guardrails | C12 | Scan outbound content before release |
| `block_request` | guardrails | C7, C12 | Hard-block on escalation-pattern match |
| `escalate_to_human` | guardrails | C7 | Doctrine/pastoral escalation to a human |
| `detect_pii` | consent | C11 | Locate PII in input/output |
| `redact_pii` | consent | C11 | Remove PII before logging |
| `log_redaction` | consent | C11 | Record that redaction occurred (no PII retained) |
| `support_dsar` | consent | C11 | Data-subject access/erasure support |
| `query_index` | rag | C2 | Tenant/locale-scoped index query |
| `retrieve_documents` | rag | C1 | Fetch from approved sources only |
| `check_source_approval` | rag | C1 | Verify a source is on the allow-list |
| `generate_draft` | content | C4 | Draft from retrieved sources only |
| `attach_provenance` | content | C4 | Attach a source citation to every claim |
| `request_editorial_approval` | content, translation | C3 | Route output to the editorial gate |
| `translate_content` | translation | C5 | Locale rendering, provenance preserved |
| `check_terminology` | translation | C5 | Terminology consistency / sensitive-term flag |
| `generate_metadata` | seo | C4 | Metadata from approved content |
| `generate_structured_data` | seo | C4 | Structured data from approved content |
| `check_keyword_fitness` | seo | — | Keyword suitability (no numbered control) |
| `validate_wcag` | accessibility | C6 | WCAG 2.1 AA validation |
| `check_alt_text` | accessibility | C6 | Alternative-text coverage |
| `check_color_contrast` | accessibility | C6 | Contrast-ratio validation |
| `block_release` | accessibility | C6 | Release gate independent of approval |
| `approve_content` | editorial | C3 | Human-approver sign-off |
| `reject_content` | editorial | C3 | Reject output failing review |
| `check_provenance_completeness` | editorial | C4 | Every claim carries a citation |
| `log_approval` | editorial | C3, C17 | Durable approval record (7-year retention) |
| `log_decision` | orchestrator, audit | C17 | Immutable decision logging |
| `hash_evidence` | audit | C4, C17 | Evidence hashing for tamper detection |
| `detect_drift` | audit, observability | — | Model/eval drift detection (monitoring) |
| `collect_telemetry` | observability | C15 | Token + cost telemetry |
| `emit_incident_signal` | observability | C16 | Incident signalling for kill-switch |
| `compose_page` | website | — | Compose site from approved, gated artefacts |
| `check_editorial_approval` | website | C3 | Verify editorial gate per artefact |
| `check_accessibility_gate` | website | C6 | Verify accessibility gate per artefact |

## Model grants

`model_policy.provider` and `model_policy.model` are `null` for all 12 agents.
Model selection is deferred to the `jolarca-vendor` DPIA (C13), so no model-invocation
tool grants exist yet. When a provider is registered, add its invocation grant here
and record the vendor risk assessment.

## Observations

Both observations were reviewed on 2026-10-01 against the agents' `policy.yaml`
files. Each verdict cites the evidence that settles it rather than reasoning alone.
The orchestrator grant/policy mismatch originally listed here was fixed in a
follow-up change and is no longer open.

1. **Shared `detect_drift` (audit + observability) — confirmed correct by design.**
   The two agents provably write to different sinks:

   | Signal | audit | observability |
   |---|---|---|
   | Store operated on | `query_audit_log` | `query_metrics` |
   | Integrity denies | `modify_audit_log`, `delete_audit_log` | `modify_telemetry`, `suppress_incident_signals` |
   | Retention | 2555 days (7 years) | 90 days |

   Divergent retention alone rules out a shared store, and observability holds no
   grant that could write to or alter the audit log — so audit evidence immutability
   (C17) is not exposed by the shared tool.

   **Residual follow-up (runtime-time, not a defect in these definitions):** both
   agents declare the same escalation pattern token `drift_detected` with
   `action: escalate`, yet they mean different things — audit drift (evidence and log
   integrity, paired with `audit_log_tampering_attempt`) versus model/eval drift
   (paired with `error_rate_spike` and `cost_ceiling_approached`). Sibling patterns
   disambiguate in context, but a runtime keying alerts on the pattern name alone
   would double-fire. Either qualify the pattern names or route escalation by
   emitting agent id.

2. **Composition over re-implementation (`website`) — confirmed correct by design.**
   `website` holds *verification* verbs only; the *producing* verbs stay with their
   owning agents and no verb overlaps:

   | Agent | Verbs |
   |---|---|
   | website | `check_editorial_approval`, `check_accessibility_gate` — consume verdicts |
   | editorial | `approve_content`, `reject_content`, `check_provenance_completeness` — produce |
   | accessibility | `validate_wcag`, `check_alt_text`, `check_color_contrast`, `block_release` — produce |

   Reinforced by the `website` denies (`publish_without_approval`,
   `use_unapproved_content`, `bypass_accessibility_gate`) with
   `escalation.action: block` — a hard fail-safe at the publishing edge — and by
   layer ordering, since `website` (Layer 6) depends on `editorial` (Layer 5) and
   `accessibility` (Layer 4). Matches the HERMES-0001 invariant; keep it that way.

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-10-01 | Initial register derived from the 12 `agent.yaml` `tool_grants` | Agent (proposed, PR review) |
| 2026-10-01 | Fixed orchestrator grant/policy mismatch; added `log_decision` to orchestrator tool_grants and `kill_switch` to policy allow.actions | Agent (PR review) |
| 2026-10-01 | Reviewed both observations against `policy.yaml` evidence; both confirmed correct by design; opened one runtime follow-up on the shared `drift_detected` pattern name | Agent (PR review) |
| 2026-10-03 | Corrected the totals sentence: it claimed 39 distinct tools while the Tool index immediately below listed 38, so the document contradicted itself. The per-agent table, the index set and the named shared tools were already accurate. Now re-derived on every test run by `tests/test_tool_register_consistency.py` | Agent (proposed, PR review) |
