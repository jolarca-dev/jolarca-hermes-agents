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

## Markdown linting

`make markdown-lint` runs the same integrity-pinned tool the CI `markdown-lint` job runs. It needs
**Node 22 or newer** — declared in `package.json` under `engines.node`, because markdownlint 0.41.1
requires it — plus the lockfile install:

```bash
npm ci --no-audit --no-fund --ignore-scripts
make markdown-lint    # 49 tracked markdown files, 0 findings expected
```

`make check` deliberately does **not** invoke it, so the pre-merge Python loop stays free of any npm
dependency. Under an older Node, npm reports `EBADENGINE`; the tool may still run, but CI will not match
what you checked locally, so install the declared major rather than trusting the warning.

## Local hooks

`.pre-commit-config.yaml` declares gitleaks, private-key, YAML, merge-conflict and
large-file checks, `trailing-whitespace`, `end-of-file-fixer`, and ruff. Hooks are **per
clone** — they run nowhere until someone installs them:

```bash
python -m pip install pre-commit
pre-commit install            # enable the git hook for this clone
pre-commit run --all-files    # run every hook now, without committing
```

No CI job runs pre-commit, so the binding gates are still the `lint`, `test` and
`security` required contexts plus the supplementary jobs. `trailing-whitespace` carries
`--markdown-linebreak-ext=md` because three governance documents open their
`**Status:**` / `**Date:**` headers with markdown hard line breaks (two trailing spaces);
without that argument, installing the hook silently fuses that compliance metadata into
one rendered paragraph. The argument is required by `tests/test_precommit_hook_safety.py`.

Never bypass a hook with `--no-verify`; fix the finding instead.

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
