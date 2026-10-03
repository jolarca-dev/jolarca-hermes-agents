# HERMES-0003: Model Sourcing, Self-Hosted Inference, and the Mission Boundary

**Status:** Proposed
**Date:** 2026-10-01
**Deciders:** jolarca-dev (solo operator)

---

## Context

C13 (model vendor risk assessment) has been driven as far as repo work allows: the
methodology exists in `jolarca-vendor`, and `onboarding` assessment skeletons exist in
`jolarca-compliance`. All three registered `ai-llm` candidates are external SaaS
providers, and closing C13 for them requires artifacts this side cannot manufacture —
a signed DPA, a returned due-diligence questionnaire, and a completed TIA. That is a
genuinely external dependency: it resolves only through negotiation with a third party.

The operator has since established self-hosted inference, which changes the picture.
Self-hosting removes the transfer and third-party-retention problem at its root — the
data does not leave infrastructure the operator controls, and EU residency for the
Lithuania / Latvia / Estonia pilot is satisfied by construction rather than by contract.

However, the inference resource the operator stands up lives on the **mission** side of
the estate, and `jolarca-hermes-agents` is a **marketplace** repository. ADR-0004 R4
mandates mission/marketplace separation and forbids marketplace repositories from
referencing mission-platform resources. That separation is enforced mechanically:
`scripts/check_deny_patterns.py` fails CI on any mission-platform token, and the
`orchestrator` and `guardrails` agent prompts refuse such references at runtime. Same
natural owner does not mean same legal or audit boundary: a marketplace runtime coupled
to a mission server would (a) fail this repository's own CI, (b) be blocked by its
guardrails, and (c) merge two audit scopes, pulling the mission inference host into the
marketplace's PCI-DSS/cardholder-data boundary and vice-versa.

This ADR records where self-hosted inference belongs and how the marketplace fleet may
source a model without violating the separation that founding the fleet.

## Decision

### 1. The marketplace fleet does not couple to mission inference

No agent in this fleet may reference, depend on, or be configured to call a
mission-platform inference resource. This is not a new rule; it reaffirms ADR-0004 R4,
which this repository already enforces. Consequently this ADR names no mission org or
repository, and none may appear in any file in this tree.

### 2. Self-hosted inference for the Baltic pilot is a mission-side concern

The pilot (Lithuania / Latvia / Estonia) and its self-hosted model server are realized
as a mission system, in a mission-owned runtime that consumes mission inference. That
work is out of scope for `jolarca-hermes-agents` and is not the consumer of this
repository's agent definitions. Should a mission-side agent fleet be needed, it is
defined on the mission side, where referencing mission infrastructure is normal rather
than forbidden.

### 3. Two compliant paths for the marketplace fleet's own model sourcing

If and when this fleet must call a model, it uses one of the following — never the
mission resource:

**Path A — marketplace-owned self-hosted inference.** Stand up inference on
marketplace (`jolarca-dev`) infrastructure as a declared, allow-listed service with
`service_model: self-hosted`. Its risk is assessed as **infrastructure risk plus model
provenance**, not as a third-party DPIA: there is no data exporter, so the DPA/TIA
chain that blocks the SaaS path does not apply. It is assessed like `proxmox` or
`hetzner` in the vendor records, plus the additional, non-trivial obligations listed in
§5.

**Path B — a third-party provider via the full C13 DPIA.** The OpenAI / Anthropic /
Google route already scaffolded: it requires the signed DPA, completed questionnaire,
and TIA. This path is gated on external vendor engagement and remains the slower one.

### 4. Providers stay null until a marketplace path completes

`model_policy.provider` remains `null` for all 12 agents. That invariant is enforced by
the `vendor-risk-check` CI job, which runs `scripts/check_vendor_risk.py` and fails if any
agent declares a provider, so the fleet cannot silently acquire one before its assessment
lands. C13 therefore stays **open for the marketplace fleet** — it is not closed by the
existence of mission-side inference, which is a different system serving a different
boundary.

### 5. Self-hosting is not governance-free

Self-hosting removes the *transfer* risk but not all risk. Path A still requires, before
any agent calls it:

- **Model provenance.** Open-weight model files are third-party supply-chain artifacts.
  Record the base-model source, license, and version pin; an unpinned downloaded weight
  set is a shadow model by another name.
- **Infrastructure security.** The serving host is a marketplace system in the PCI-DSS
  boundary: hardening, access control, logging, and secrets management apply as they
  would to any inference endpoint.
- **Data-classification fit.** The agent tiers that call it (`content`, `seo`,
  `translation` generation; `guardrails` inspection) already declare a maximum data
  classification; the endpoint must honor it.
- **Framework ADR.** Runtime orchestration selection stays blocked on this decision and
  is recorded separately once Path A or Path B is chosen, preserving the ordering
  constraint in `jolarca-vendor` `VEN-0001` (assessment before framework, not after).

## Consequences

### Positive

- The external C13 deadlock is escaped without weakening the separation control: the
  fast, residency-clean route (self-hosting) is available to the marketplace via Path A
  on its own infrastructure.
- No forbidden token is introduced; CI, guardrails, and ADR-0004 R4 stay intact and
  still meaningful.
- Audit scopes remain clean: mission data and marketplace cardholder-data scope do not
  commingle.

### Negative

- The marketplace fleet's model sourcing is still not decided; C13 remains open here.
- Path A moves effort from "negotiate a DPA" to "operate hardened inference + assess
  model provenance," which is real work, not a free pass.

### Risks

- Treating "self-hosted" as automatically compliant and skipping model-provenance and
  infrastructure assessment — mitigated by §5, which is explicit that self-hosting
  changes the risk type, it does not remove it.
- Pressure to reference the mission server for convenience — mitigated by the
  deny-pattern scanner and guardrail prompts, which fail this repo mechanically on any
  such reference; exclusions must not be widened to permit it.
- The Baltic pilot being assumed to run on this fleet — mitigated by §2: the pilot is a
  mission system; this repository is not its runtime.

---

## Compliance Mapping

| Aspect | SOC 2 | ISO 27001 | GDPR |
|---|---|---|---|
| Mission/marketplace boundary (§1) | CC3.2, CC9.2 | A.5.9, A.5.19 | Art. 5(1)(b), Art. 44 |
| Self-hosted Baltic pilot is mission-side (§2) | CC6.1 | A.5.23 | Art. 44 (residency by construction) |
| Path A self-hosted assessment (§3) | CC9.2, CC6.1 | A.5.19, A.5.21, A.12.6 | Art. 28(1), Art. 32 |
| Providers stay null (§4) | CC7.1, CC8.1 | A.8.16, A.5.19 | Art. 5(1)(a) |
| Model provenance + infra (§5) | CC8.1, CC6.8 | A.5.21, A.8.30 | Art. 32 |

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-10-01 | Initial ADR (proposed) | Agent (pending operator acceptance on merge) |
| 2026-10-03 | §4 corrected to name `vendor-risk-check` as the enforcement locus for the null-provider invariant. When this ADR was written, `check_vendor_risk.py` existed and passed locally but was invoked by no CI job, so the assertion it describes was not actually enforced; that job is now wired | Agent (proposed, pending operator acceptance) |
