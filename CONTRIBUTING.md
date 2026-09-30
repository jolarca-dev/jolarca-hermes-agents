# Contributing to jolarca-hermes-agents

This repository is a **public** compliance artifact of the `jolarca-dev`
marketplace fleet. It contains AI agent implementations that operate under
SOC 2 Type II, ISO 27001:2022, and GDPR controls.

## The invariants

1. **No mission-platform references.** ADR-0004 R4 forbids any reference to
   the mission GitHub organization, mission-prefixed repositories, or mission
   local paths. Enforced by `scripts/check_deny_patterns.py`.
2. **Every agent has an identity tag.** Tags follow `agent:jolarca:<module-id>`.
   Untagged agents are rejected by `scripts/validate_agents.py`.
3. **Every control has an enforcement mechanism.** A control without a failing
   CI job is folklore (ADR-0004 R3). See `docs/control-matrix.md`.

## Before you commit

```bash
make check    # lint + validate + deny-patterns
```

## Agent changes

When adding or modifying an agent:

1. Update `agent.yaml` with the identity tag and model policy
2. Update `policy.yaml` with allow/deny rules
3. Add tests in `agents/<name>/tests/`
4. Run `make validate` to check schemas
5. Update `docs/capability-map.md` if adding a new agent

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

Do NOT commit credentials, tokens, API keys, or cryptographic key material.
