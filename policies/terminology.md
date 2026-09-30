# Terminology Registry

**Status:** Active
**Owner:** `translation` agent
**Control:** C5 (translation review for sensitive content)
**Last reviewed:** 2026-09-30

---

## Purpose

This registry defines approved translations for domain-specific terms. The
`translation` agent checks all translations against this registry to ensure
terminology consistency across locales.

## Approval Criteria

A term is approved when:

1. **Domain accuracy** — The translation accurately represents the domain concept.
2. **Consistency** — The term is used consistently across all content.
3. **Cultural appropriateness** — The translation is appropriate for the target locale.
4. **No doctrinal ambiguity** — For religious/liturgical terms, the translation
   has been reviewed by a human authority.

## Registry

Terms are organised by domain. Each entry includes the source term (English),
the approved translation, the target locale, and the approval date.

### Marketplace Terms

| Source (en) | Translation | Locale | Approved |
|---|---|---|---|
| marketplace | rinka | lt | 2026-09-30 |
| agent | agentas | lt | 2026-09-30 |
| fleet | laivynas | lt | 2026-09-30 |
| compliance | atitiktis | lt | 2026-09-30 |
| governance | valdysena | lt | 2026-09-30 |

### Technical Terms

| Source (en) | Translation | Locale | Approved |
|---|---|---|---|
| identity tag | tapatybes zyma | lt | 2026-09-30 |
| provenance | kilme | lt | 2026-09-30 |
| retention | saugojimo laikas | lt | 2026-09-30 |
| escalation | eskalacija | lt | 2026-09-30 |

### Sensitive Terms (Human-Reviewed)

| Source (en) | Translation | Locale | Reviewed By | Approved |
|---|---|---|---|---|
| doctrinal | doktrininis | lt | human | 2026-09-30 |
| pastoral | ganyvistinis | lt | human | 2026-09-30 |
| liturgical | liturginis | lt | human | 2026-09-30 |

## Adding a Term

To add a new approved term:

1. Submit a PR adding a row to the appropriate table.
2. Include: source term, translation, locale, approval date.
3. Sensitive terms require human review before approval.
4. The `translation` agent's `check_terminology` tool validates against this list.

## Unapproved Terms

Terms not in this registry are flagged by the `translation` agent and
escalated for review. Content with unapproved terms is held until the
terminology is resolved.

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-09-30 | Initial terminology registry (Lithuanian) | Agent (pending review) |
