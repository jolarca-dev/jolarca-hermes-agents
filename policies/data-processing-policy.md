# Data Processing Policy

**Status:** Active
**Owner:** `consent` agent
**Control:** C10 (policy separation), C11 (PII redaction)
**Last reviewed:** 2026-10-01

---

## Purpose

This policy defines how data is classified, handled, and processed across
the Hermes agent fleet. It establishes the data classification scheme,
handling rules per classification, and the GDPR legal bases for processing.

This policy is separate from the mission platform's data-processing policy
(ADR-0004 R1: institutional independence).

---

## Data Classification Scheme

Every piece of data processed by the fleet falls into one of four
classifications:

| Classification | Definition | Examples | Agents |
|---|---|---|---|
| **restricted** | Data that causes severe harm if disclosed. PII, credentials, legal holds. | Email addresses, names, authentication tokens, DSAR records | consent |
| **confidential** | Data that causes moderate harm if disclosed. Internal documents, generated content, approval records. | Drafts, retrieval results, editorial decisions, provenance records | rag, content, translation, editorial, audit |
| **internal** | Data intended for internal use only. Operational metadata, telemetry, configuration. | Agent configs, budget logs, telemetry, deny-pattern rules | orchestrator, guardrails, observability |
| **public** | Data approved for external publication. Final website content, metadata, accessibility reports. | Published pages, SEO metadata, WCAG reports | seo, accessibility, website |

## Handling Rules

### Restricted Data

- **Encryption:** Must be encrypted in transit (TLS 1.2+) and at rest
  (AES-256).
- **PII redaction:** All PII must be redacted before logging. The `consent`
  agent performs redaction (C11).
- **No cross-tenant access:** Restricted data from tenant A must never be
  accessible to tenant B (C2).
- **Retention:** Maximum 30 days for PII redaction logs; 7 years for DSAR
  records (see `policies/retention.md`).
- **Transmission:** Must not appear in logs, error messages, or telemetry
  in plaintext.

### Confidential Data

- **Source restriction:** May only be retrieved from approved sources (C1).
- **Provenance:** Every claim derived from confidential data must carry a
  source citation (C4).
- **Editorial gate:** Content derived from confidential data requires
  editorial approval before publication (C3).
- **Retention:** 90 days for operational data; 7 years for editorial
  approval records.
- **Model exposure:** May only be sent to an approved LLM provider (see
  `policies/model-policy.md`).

### Internal Data

- **Access control:** Accessible only to agents with `internal` or higher
  classification.
- **No external publication:** Must not appear in public-facing output
  without transformation through the editorial gate.
- **Retention:** 90 days for operational logs and telemetry.
- **Budget tracking:** Token usage and cost data are internal; tracked by
  the `orchestrator` agent (C15).

### Public Data

- **editorial gate required:** Data may only become public after passing
  through the `editorial` agent's approval workflow (C3).
- **Accessibility validation:** Public web content must pass the
  `accessibility` agent's WCAG 2.1 AA checks before release (C6).
- **No PII in public output:** The `consent` agent must verify no PII
  leaks into public content.

## Classification Flow

Data can be promoted to a higher classification only through a human gate:

```
restricted → [consent redaction] → confidential
confidential → [editorial approval] → public
internal → [editorial approval] → public
```

Data is never downgraded automatically. A human must approve any
reclassification.

---

## GDPR Legal Bases for Processing

Each processing activity must have a documented legal basis under GDPR
Art. 6:

| Processing Activity | Legal Basis | GDPR Article | Agent |
|---|---|---|---|
| Content generation from approved sources | Legitimate interest | Art. 6(1)(f) | content |
| Translation of approved content | Legitimate interest | Art. 6(1)(f) | translation |
| SEO metadata generation | Legitimate interest | Art. 6(1)(f) | seo |
| WCAG accessibility validation | Legal obligation | Art. 6(1)(c) | accessibility |
| PII redaction and DSAR handling | Legal obligation | Art. 6(1)(c) | consent |
| Audit logging | Legitimate interest | Art. 6(1)(f) | audit |
| Telemetry and monitoring | Legitimate interest | Art. 6(1)(f) | observability |
| Budget tracking | Legitimate interest | Art. 6(1)(f) | orchestrator |
| Prompt injection defence | Legitimate interest | Art. 6(1)(f) | guardrails |
| Doctrinal escalation | Vital interests / Art. 9 | Art. 6(1)(d), Art. 9(2)(c) | guardrails |

### Special Category Data (GDPR Art. 9)

The fleet may encounter special category data (religious beliefs, pastoral
queries) in the course of marketplace content processing. When this occurs:

1. The `guardrails` agent escalates to a human (C7).
2. No automated decision-making is applied to special category data.
3. Special category data is never stored in logs or telemetry.
4. The `consent` agent redacts any special category data that appears in
   processing output.

## Data Subject Rights (GDPR Chapter III)

| Right | Implementation | Agent |
|---|---|---|
| Art. 15 — Access | DSAR workflow retrieves all data for a subject | consent |
| Art. 16 — Rectification | Correct inaccurate data in approved sources | consent |
| Art. 17 — Erasure | Delete PII within 30 days; generate deletion certificate | consent |
| Art. 20 — Portability | Export data in machine-readable format | consent |
| Art. 21 — Object | Halt processing pending review | consent |
| Art. 22 — Automated decisions | No automated decision-making; human gates on all substantive actions | all agents |

---

## Prohibited Processing

1. **No processing without legal basis.** Every processing activity must
   map to an Art. 6 basis (see table above).
2. **No processing of special category data without Art. 9 condition.**
   Religious content triggers escalation (C7), not automated processing.
3. **No cross-tenant data mixing.** Tenant data is isolated at the index
   level (C2).
4. **No data transfer outside approved jurisdictions.** See
   `policies/model-policy.md` for provider data residency requirements.
5. **No retention beyond scheduled periods.** See `policies/retention.md`.

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-10-01 | Initial data processing policy | Agent (accepted by solo operator) |
