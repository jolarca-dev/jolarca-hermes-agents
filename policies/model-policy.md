# Model Policy

**Status:** Active
**Owner:** `orchestrator` agent
**Control:** C13 (model vendor risk assessment)
**Last reviewed:** 2026-10-01

---

## Purpose

This policy defines the criteria for selecting, approving, and operating LLM
providers within the Hermes agent fleet. No LLM provider is currently
selected. When one is selected, it must satisfy every requirement in this
policy before processing any data.

## Current State

All 12 agents declare `model_policy.provider: null` and `model_policy.model: null`.
No model calls are made. This policy is the precondition for provider selection.

## Selection Criteria

A model provider is approved when **all** of the following are satisfied:

### 1. Data Processing Agreement (DPA)

- The provider offers a written DPA compliant with GDPR Art. 28.
- The DPA covers sub-processor transparency (Art. 28(2)).
- The DPA specifies data residency within the EU or an adequacy-decided
  country (GDPR Art. 45).

### 2. Data Protection Impact Assessment (DPIA)

- A completed DPIA is registered in the `jolarca-vendor` repo before any
  data is sent to the provider.
- The DPIA covers: purpose limitation, data minimisation, retention limits,
  data subject rights, and cross-border transfer safeguards.
- The DPIA is reviewed annually or when the provider's processing changes.

### 3. Security Posture

- The provider holds at minimum SOC 2 Type II or ISO 27001 certification.
- The provider demonstrates encryption in transit (TLS 1.2+) and at rest
  (AES-256 or equivalent).
- The provider has a documented incident response procedure with notification
  within 72 hours (GDPR Art. 33).

### 4. Operational Requirements

- The provider offers API-level access controls (API keys, service accounts).
- The provider guarantees no training on customer data (opt-out or
  contractually binding zero-retention).
- The provider offers rate limiting and usage metering to support budget
  ceilings (C15).

### 5. Model Capability

- The model must support the languages in scope (English, Lithuanian).
- The model must handle structured output (JSON, YAML) reliably.
- The model's context window must accommodate the largest agent prompt plus
  expected retrieval context.

## Provider Registry

| Provider ID | Provider Name | Model | DPA Signed | DPIA Completed | Approved |
| --- | --- | --- | --- | --- | --- |
| *(none yet)* | — | — | — | — | — |

No provider is approved. Do not send data to any LLM until a row appears
in this table with all columns filled.

## Per-Agent Model Assignment

When a provider is approved, each agent will be assigned a model based on
its role:

| Agent | Model Tier | Rationale |
| --- | --- | --- |
| orchestrator | none | Delegates; does not call models directly |
| guardrails | inspection | Pattern matching only; no generation |
| consent | none | Redaction logic; no generation |
| rag | none | Retrieval only; no generation |
| content | generation | Draft generation from retrieved sources |
| translation | generation | Locale rendering with provenance preservation |
| seo | generation | Metadata and structured data generation |
| accessibility | none | WCAG rule validation; no generation |
| editorial | none | Review workflow; no generation |
| audit | none | Immutable logging; no generation |
| observability | none | Telemetry analysis; no generation |
| website | none | Composition only; no generation |

Agents marked "none" do not require a model assignment. Only agents marked
"generation" or "inspection" will be assigned a model.

## Prohibited Practices

1. **No shadow models.** An agent must not call a model not listed in the
   provider registry. Enforced by deny-pattern scan (C8).
2. **No training on our data.** Contract must explicitly prohibit the
   provider from using our inputs/outputs for model training.
3. **No cross-tenant data leakage.** The provider's API must support
   tenant-scoped requests or the agent must enforce isolation before
   sending data.
4. **No unvetted endpoints.** Only the provider's official API endpoint
   is permitted. Proxies, mirrors, and third-party wrappers require
   separate DPIA.

## DPIA Trigger Events

A new or updated DPIA is required when:

- A new provider is selected
- An existing provider changes their data processing practices
- A new agent role is added that changes the data processing scope
- Data residency requirements change (e.g., new tenant jurisdiction)
- A security incident occurs at the provider

## Vendor Risk Review Cadence

- **Initial review:** Before first data is sent.
- **Annual review:** At minimum once per 12 months.
- **Event-driven review:** Within 30 days of a trigger event.
- Review records are stored in `jolarca-vendor` repo.

---

## Revision History

| Date | Change | Authority |
| --- | --- | --- |
| 2026-10-01 | Initial model policy (no provider selected) | Agent (accepted by solo operator) |
