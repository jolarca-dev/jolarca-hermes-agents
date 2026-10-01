# Architecture Decision Records — Index

**ADR prefix:** HERMES-
**Namespace allocated in:** `jolarca-docs/adr/namespace.md`

---

## Records

| ADR | Title | Status | Date |
|---|---|---|---|
| [HERMES-0001](HERMES-0001-agent-architecture.md) | Agent Architecture — Identity Tags, Build Order, and Gate Types | Accepted | 2026-09-30 |
| [HERMES-0002](HERMES-0002-evaluations-and-tool-register.md) | Adversarial Evaluations and Consolidated Tool Register | Proposed | 2026-10-01 |
| [HERMES-0003](HERMES-0003-model-sourcing-and-mission-boundary.md) | Model Sourcing, Self-Hosted Inference, and the Mission Boundary | Proposed | 2026-10-01 |

---

## Conventions

- **Prefix:** All ADRs in this repository use the `HERMES-` prefix (allocated via `jolarca-docs`).
- **Numbering:** Sequential, zero-padded to 4 digits (e.g., `HERMES-0001`).
- **Naming:** `HERMES-NNNN-short-title.md` (lowercase, hyphen-separated).
- **Status lifecycle:** `Proposed` → `Accepted` → `Deprecated` (or `Superseded by HERMES-XXXX`).
- **Template:** Use [TEMPLATE.md](TEMPLATE.md) for new ADRs.
- **Authority:** In the solo-operator era, the operator is the accepting authority. When teams are created, update the authority field per ADR.

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-10-01 | Initial ADR index | Agent (accepted by solo operator) |
| 2026-10-01 | Added HERMES-0002 (index drift fix) and HERMES-0003 | Agent (pending operator acceptance on merge) |
