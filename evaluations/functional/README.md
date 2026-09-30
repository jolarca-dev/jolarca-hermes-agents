# Functional Evaluations

**Status:** Deferred — not yet populated.

Functional evaluations assert that a benign request produces the intended
end-to-end behaviour (routing, delegation, drafting, composition). They require
a **running agent runtime**, which does not exist yet: this repository is the
declarative source of agent definitions, and `model_policy.provider` is `null`
across all 12 agents (C13 deferred to `jolarca-vendor`).

## Trigger to populate

Create `functional/cases.yaml` when either:

1. an agent runtime is available to execute a request, or
2. a model provider is registered and live replay becomes possible.

## Contract

Follow `schemas/eval-case.schema.json` (see `../README.md`). Functional cases map
to the relevant agent `allow.actions` with `expected_action: allow`, and set the
`control` field only where a control applies. Structural and policy checks that
need no runtime already live in `scripts/check_*.py` and are not duplicated here.
