# Retention Policy

**Status:** Active
**Owner:** `audit` agent
**Control:** C14 (output retention and deletion schedule)
**Last reviewed:** 2026-09-30

---

## Purpose

This policy defines retention periods for all data types processed by the
Hermes agent fleet. Retention periods are driven by compliance requirements
(SOC 2, ISO 27001, GDPR) and operational needs.

## Retention Schedule

| Data Type | Retention Period | Rationale | Agent |
|---|---|---|---|
| Audit logs | 7 years (2555 days) | SOC 2 CC7.2, ISO 27001 A.8.10 | audit |
| Editorial approval records | 7 years (2555 days) | SOC 2 CC8.1 | editorial |
| Agent decision logs | 90 days | Operational debugging | all agents |
| Telemetry (tokens, cost) | 90 days | Operational monitoring | observability |
| Retrieved documents | 90 days | RAG cache | rag |
| Generated drafts | 90 days | Editorial workflow | content |
| PII redaction logs | 30 days | GDPR Art. 5(1)(e) | consent |
| Incident signals | 1 year | Operational review | observability |
| DSAR records | 7 years | GDPR accountability | consent |

## GDPR Art. 17 (Right to Erasure)

Personal data must be deleted when:

- The purpose for which it was collected no longer applies
- The data subject withdraws consent
- The data subject exercises their right to erasure

The `consent` agent handles DSAR requests and enforces erasure within 30 days.

## Deletion Procedure

1. Data past its retention period is flagged for deletion.
2. The `audit` agent logs the deletion event.
3. Deletion is permanent and irreversible.
4. A deletion certificate is generated (hash of deleted records).

## Exceptions

Retention may be extended when:

- Legal hold is in place (litigation, investigation)
- Regulatory requirement demands longer retention
- Business justification is recorded and approved

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-09-30 | Initial retention policy | Agent (pending review) |
