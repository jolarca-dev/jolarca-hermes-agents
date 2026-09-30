# Approved Sources Registry

**Status:** Active
**Owner:** `rag` agent
**Control:** C1 (approved sources only)
**Last reviewed:** 2026-09-30

---

## Purpose

This registry defines the sources from which the `rag` agent may retrieve
documents. Only sources listed here are approved for retrieval. Unapproved
sources are rejected at retrieval time.

## Approval Criteria

A source is approved when:

1. **Content ownership** — The source is owned or licensed by jolarca-dev.
2. **Quality assurance** — Content has passed editorial review.
3. **Provenance integrity** — Source provides reliable citation metadata.
4. **Data classification** — Source classification is compatible with the
   agent's classification (confidential or lower).
5. **GDPR compliance** — No personal data without lawful basis for processing.

## Registry

| Source ID | Source Type | Description | Classification | Approved |
|---|---|---|---|---|
| `jolarca-docs` | approved_document | Fleet compliance documentation (jolarca-docs repo) | internal | 2026-09-30 |
| `jolarca-control` | approved_document | Governance control plane (jolarca-control repo) | internal | 2026-09-30 |
| `jolarca-security` | approved_document | Security policies and procedures | internal | 2026-09-30 |

## Adding a Source

To add a new approved source:

1. Submit a PR adding a row to the registry table above.
2. Include: source ID, type, description, classification, approval date.
3. The PR must be reviewed by the compliance authority.
4. The `rag` agent's `check_source_approval` tool validates against this list.

## Removing a Source

To remove a source:

1. Submit a PR removing the row.
2. Record the removal date and rationale in the revision history.
3. The `rag` agent immediately stops retrieving from removed sources.

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-09-30 | Initial registry (3 sources) | Agent (pending review) |
