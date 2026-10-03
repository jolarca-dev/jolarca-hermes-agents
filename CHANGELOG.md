# Changelog

All notable changes to `jolarca-hermes-agents` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed — 2026-10-03

- Qualified the colliding `drift_detected` escalation pattern token **per emitter**: `audit`
  now declares `audit_log_drift_detected` and `observability` declares
  `model_eval_drift_detected`. This closes the runtime follow-up opened in
  `docs/tool-register.md` on 2026-10-01, which PR #30's ratchet was built to force shut.
  Renaming was checked before doing it: `git grep drift_detected` matched only the two
  `policy.yaml` files plus prose — no script, test or eval case consumed the token — and the
  new names follow the vocabulary already sitting beside them in the same files
  (`audit_log_tampering_attempt`, `error_rate_spike`, `cost_ceiling_approached`). The shared
  `detect_drift` **tool** is deliberately unchanged and remains correct by design (same verb,
  different sinks); only the alert *name* collided.
- `tests/test_escalation_pattern_uniqueness.py` tightened from a ratchet to **zero
  tolerance**. `KNOWN_COLLISIONS` is now empty and `test_debt_register_stays_empty` forbids
  adding entries. A non-empty whitelist leaves a loophole that only mattered while debt
  existed: register a new collision and both the "no new collision" and "no stale entry"
  tests pass. With the debt paid, any collision a two-agent share now fails CI outright, and
  granting an exception has to be an explicit decision rather than a line in a register.

### Added — 2026-10-03

- `tests/test_escalation_pattern_uniqueness.py`: a **ratchet** guard on escalation pattern
  tokens. Measured on main, the twelve agents declare 28 distinct `escalation.patterns`
  tokens and exactly one is shared: `drift_detected`, used by `audit` for evidence and
  audit-log integrity (alongside `audit_log_tampering_attempt`) and by `observability` for
  model/eval drift (alongside `error_rate_spike`, `cost_ceiling_approached`). Two different
  incidents carrying one name means a runtime that routes alerts on pattern name alone
  double-fires. This has been carried as prose in `docs/tool-register.md` since PR #17 with
  nothing keeping it from spreading; now any new collision fails CI.

  Built as a shrink-only baseline (`KNOWN_COLLISIONS`) rather than a blanket uniqueness rule,
  because the two directions were verified to behave differently: a **new** collision fails
  `test_no_new_escalation_pattern_collisions`, and **retiring** the listed one fails
  `test_baseline_cannot_silently_absorb_the_debt` until the baseline entry is deleted. So the
  existing debt cannot be absorbed as normal and cannot grow. Both were proven by mutation on
  throwaway edits to `agents/observability/policy.yaml`, restored with `agents/` verified
  clean.

  Renaming was deliberately **not** done here, though it is mechanically safe: `git grep
  drift_detected` matches only the two `policy.yaml` files plus prose in `CHANGELOG.md` and
  `docs/tool-register.md` — no script, test or eval case consumes the token. The replacement
  names are control vocabulary owned by the operator. Suggested, matching house style
  (`audit_log_tampering_attempt`, `error_rate_spike`): `audit_log_drift_detected` for audit
  and `model_eval_drift_detected` for observability, deleting the baseline entry in the same
  change.

- The same suite also asserts every agent's `escalation.action` is one of `block` /
  `escalate`. A typo there would silently disable an escalation while still parsing as valid
  YAML — the guard is on the vocabulary, not just the shape.

### Added — 2026-10-03

- `tests/test_tool_grant_policy_parity.py`: asserts that every entry in an agent's
  `agent.yaml` `tool_grants` also appears in that same agent's `policy.yaml`
  `allow.actions`, so no agent can hold a callable tool its own policy does not permit.
  Previously nothing compared the two lists. `tool_grants` was read by
  `scripts/check_kill_switch.py` and, since PR #25, by
  `tests/test_tool_register_consistency.py` — neither of which checks a grant against the
  same agent's `allow.actions`. Plus a guard that no agent
  has an empty grant or allow set (an empty allow list would make the subset test pass
  vacuously) and a non-vacuity test on the parser.

  The relation asserted is **one-way, because that is what the fleet measures**. Across
  the twelve agents only `orchestrator` has the two sets equal; the other eleven have
  `tool_grants` as a strict subset of `allow.actions` (tally: 11 subset, 1 equal).
  Asserting equality would fail eleven of twelve agents and state the wrong rule: least
  privilege is breached by a grant the policy does not permit, never by a permitted action
  the agent was never handed as a callable tool.

  Zero violations exist today, so the guard arrives green. Mutation-proven: injecting an
  escaping grant into `seo` failed exactly
  `test_every_granted_tool_is_permitted_by_that_agent_policy` (1 failed, 2 passed), and the
  injected file was restored with `agents/` verified clean.

### Added — 2026-10-03

- Python formatting is now **enforced** rather than merely declared. `make lint` gained
  `ruff format --check .` and the required CI `lint` job gained a matching
  `Ruff format check` step. Seven files were reformatted so the gate arrives green: four
  pre-existing (`scripts/check_deny_patterns.py`, `scripts/validate_agents.py`,
  `tests/test_deny_patterns.py`, `tests/test_validate_agents.py`), two of this workstream's own
  earlier guard suites (`tests/test_ci_gates_are_real.py` from PR #20,
  `tests/test_ci_hardening.py` from PR #23), and the new suite itself. Every join stays inside
  `line-length = 120`, so `ruff check` still passes — measured, not assumed, because formatting
  merges split string literals into longer single lines.
- `tests/test_lint_gate_scope.py`: pins that **both** the Makefile `lint` recipe and the
  required CI `lint` job run `ruff check` *and* `ruff format --check`, that formatting did not
  crowd out `validate_agents.py` or `check_deny_patterns.py` in that job, and that the two
  parsers actually found commands (non-vacuity). Written first: 3 of 4 failed. Mutation-proven
  after: deleting the step from `ci.yml` fails exactly `test_ci_lint_job_verifies_formatting`;
  deleting the Makefile line fails three.

### Changed — 2026-10-03

- `Makefile`: two comments claimed CI invokes make — the header ("CI job `lint` runs
  `make check`") and the `check` target's help text ("Full pre-merge check (CI runs this)").
  **Both false**: the job invokes `ruff check .`, `python scripts/validate_agents.py` and
  `python scripts/check_deny_patterns.py` as three explicit steps and never calls make. The
  claim was not cosmetic: had it been true, adding the formatting gate to the Makefile alone
  would have sufficed; because it is false, a Makefile-only change binds nothing in CI. That
  is precisely the "control that exists but runs nowhere" defect ADR-0004 R3 targets, so the
  gate is wired in both places and both comments rewritten. `QODER.md` §7.1 and §7.2 corrected
  to match, and §7.12 gains the corresponding drift row.

### Changed — 2026-10-03

- **Governance acceptance.** `docs/adr/HERMES-0002-…`, `docs/adr/HERMES-0003-…` and
  `QODER.md` moved from `Proposed` to `Accepted` on the operator's instruction, and
  `docs/adr/README.md`'s index statuses updated with them. Acceptance was not a rubber
  stamp: each document's in-repo claims were re-verified against the tree immediately
  beforehand, and each one's Revision History now records which claims were checked.
  Confirmed at the moment of acceptance — 12 agents with `model_policy.provider` null for
  all twelve; `vendor-risk-check` present and running `scripts/check_vendor_risk.py`;
  `deny-pattern-scan` failing CI on a mission-platform token; eval cases schema-validated
  inside the required `test` job; `adversarial-evals` still supplementary; branch
  protection still `lint`/`test`/`security`; and `QODER.md` §7.1's figures (12 agents,
  17 controls, 4 schemas, 17 scripts, 15 CI jobs) plus its statement that `make check`
  excludes tests.
- Two claim classes were **not** verified and are recorded as unverified rather than
  attested: the `jolarca-vendor` statement that all three registered `ai-llm` candidates are
  external SaaS, which is outside this repository, and anything about mission-side inference,
  which ADR-0004 R4 forbids this tree from referencing at all.
- **C13 stays open.** Accepting HERMES-0003 records the sourcing boundary; it registers no
  provider, and `vendor-risk-check` would fail if one appeared without an assessment. The
  document's `**Date:**` fields were left at their original 2026-10-01 values, matching
  HERMES-0001's accepted header; acceptance dates live in the Revision History.
- `docs/adr/HERMES-0002-…`: its two Revision History rows were swapped back into
  chronological order. The row added in this workstream had been placed above the 2026-10-01
  row, which broke the oldest-first ordering every other revision table in the repo uses.

### Added — 2026-10-03

- `tests/test_tool_register_consistency.py`: re-derives every figure `docs/tool-register.md`
  states from the twelve `agent.yaml` files — the totals sentence (grants / agents /
  distinct), each agent's grant row, the Tool index set in **both** directions, and the
  enumerated shared tools. Closes the `QODER.md` drift class "an agent grants a tool the
  register does not list", which previously had no automated check. Includes a non-vacuity
  test so a parser that stops matching fails loudly rather than passing trivially.
  Written first and observed failing on precisely one assertion
  (`register claims 39 distinct tools; the fleet grants 38`) with the other four already
  green — which is what proved the defect was a single prose figure, not a broken register.

### Fixed — 2026-10-03

- `docs/tool-register.md`: the totals sentence claimed **39 distinct tools** while the Tool
  index immediately below it lists **38**, so the document contradicted its own table. The
  register declared "if this register and an `agent.yaml` disagree, the `agent.yaml` wins"
  and nothing checked it. Corrected to 38. Everything else was already accurate: the
  per-agent rows sum to 41, the index set equals the granted set exactly with no phantom and
  no omission, and the three named shared tools match the measured duplicates.
  Root cause, reconstructed from history: when the orchestrator gained `log_decision`, that
  tool was **already** granted elsewhere, so distinct stayed 38 while grants went 40 → 41 —
  but both counters were incremented together. Two derived figures drifting in lockstep is
  the tell that they were edited by assumption rather than recomputed; the new guard
  recomputes them.
- `docs/adr/HERMES-0002-…`: §3 described the register as consolidating "all **40**
  `tool_grants`" — stale by one, since the orchestrator gained a grant after the ADR was
  drafted — and still named the orchestrator grant/policy mismatch as a recorded observation
  when that mismatch had been fixed and removed from the register. Both corrected. §Risks
  now names the automated guard, and records that declarative precedence alone was
  insufficient: the totals sentence drifted and nothing failed.

### Fixed — 2026-10-03

- `scripts/validate_agents.py`: the module docstring claimed the script validated agent and
  policy files "against JSON Schemas" and listed "Required fields present per schema". It
  never did. The script is a hand-rolled structural and identity-tag validator; the schema
  files were only opened by `load_schema()`, a function defined and **never called**
  anywhere in the repository. The docstring now states what the script actually checks and
  names `tests/test_schemas.py` — which runs in the required CI `test` job — as where Draft
  2020-12 conformance is asserted, so the two complementary checks are discoverable instead
  of conflated. The dead helper and its now-unused `json` import and `SCHEMAS_DIR` constant
  are removed. Behaviour is unchanged: 12 agents still validate, exit 0.

  Deliberately **not** fixed by making the script schema-validate. `test` is already a
  branch-protection required context, so schema conformance was never unenforced — only
  misdocumented. Adding real validation here would mean installing `jsonschema` into the
  `lint` and `agent-policy-guard` jobs to duplicate coverage that already gates merges.

### Added — 2026-10-03

- `.github/workflows/ci.yml`: a `secrets-scan` job running the gitleaks CLI over the **full
  git history** (`fetch-depth: 0`, `--log-opts="--all"`). Before this, nothing executed
  gitleaks anywhere: `.pre-commit-config.yaml` declared the hook but the hooks have never
  been installed (`.git/hooks` holds no non-sample files) and no CI job invoked it, so the
  control `SECURITY.md` asserts was folklore under ADR-0004 R3 — corroborated by
  `.gitleaksignore`, which still read "No known false positives yet" because the scanner
  had never produced any output. It installs a checksum-verified release binary rather than
  `gitleaks/gitleaks-action`, which requires a `GITLEAKS_LICENSE` secret for
  organisation-owned repositories and fails on every run (fleet finding F-01 in
  `jolarca-security`). Measured before wiring: gitleaks 8.30.1 scanned the working tree and
  all 23 commits and reported **no leaks**, exit 0. The job is **supplementary** rather
  than folded into the required `security` context because the sha256 it pins is inherited
  from a `jolarca-security` workflow whose only recorded run failed on 2026-09-26 and has
  never executed since the fix, so this job is the digest's first real verification; a wrong
  digest then surfaces as one red job with a one-line correction instead of a merge outage.
  Promoting it to a required check is a separate decision — required contexts are
  Terraform-managed in `jolarca-control`.
- `tests/test_ci_hardening.py`: guards that every action reference is pinned to a full
  40-character commit SHA carrying a version comment, that each workflow declares
  least-privilege `permissions`, and that the secret scanner is wired, licence-free,
  checksum-verified and history-scanning — plus a non-vacuity test on the reference parser.
  Written first and observed failing on all four live defects.

### Changed — 2026-10-03

- `.github/workflows/ci.yml`: every action reference moved from a mutable major version tag
  to a full commit SHA annotated with its resolved version, so an upstream tag retarget
  cannot silently change what the pipeline executes. `actions/checkout` advances v4 to v7
  and `actions/setup-python` v5 to v7, superseding dependabot PRs #4 and #5, which proposed
  those same versions and were green. Both refs were resolved to commit SHAs before
  pinning: `gitleaks`-style tags can point at an annotated tag *object*, and GitHub Actions
  rejects both that and abbreviated SHAs.
- `.github/workflows/ci.yml`: added a workflow-level `permissions: { contents: read }`
  block. No workflow previously declared one, leaving `GITHUB_TOKEN` scoped by the
  organisation default rather than a stated ceiling.
- `QODER.md` and `README.md`: job count 14 to 15, and §7.10 no longer claims CI runs no
  secret-scanning job. §7.10 now also warns that the `trailing-whitespace` hook conflicts
  with the deliberate two-space markdown hard breaks used by governance doc header blocks.

### Added — 2026-10-03

- `QODER.md`: behavioural contract for AI-assisted changes in this repository. Sections
  1-6 carry the four general anti-hallucination principles plus two that this repository's
  own doctrine demands — "enforced, not documented" (ADR-0004 R3) and dual-state honesty —
  because a definition-only fleet whose `security` gate could not fail is exactly what
  those principles exist to catch. Section 7 records verified repo-specific rules: the
  deny-pattern scanner's exemption list and its prose-match trap, the schema and
  identity-tag contracts, where schema validation actually runs versus where its docstring
  claims it runs, the CI wiring invariants, gate failure behaviour, and a definition-of-done
  checklist. Factual claims were measured against the tree rather than asserted, and
  figures that age are flagged for re-verification instead of quoted as truth. Follows the
  `QODER.md` convention already used by five sibling repositories in the fleet.
- `.github/workflows/ci.yml`: wired the eight `scripts/check_*.py` enforcement scripts that
  existed and passed standalone but were invoked by no CI job, which left C1, C2, C3, C4,
  C5, C7, C12 and C13 folklore under ADR-0004 R3 ("a control without a failing CI job is
  folklore"). Two supplementary jobs were created — `provenance-check` (C3 editorial
  approval, C4 source provenance) and `vendor-risk-check` (C13 model vendor risk and the
  null-provider invariant) — making the job names `docs/control-matrix.md` already cited
  real, and five control steps were added to `agent-policy-guard` (C1 approved sources,
  C2 tenant isolation, C5 translation review, C7 doctrine escalation, C12 injection
  defence) to match the coverage that matrix already attributed to it. Job count 12 → 14.
  The three required status checks (`lint`, `test`, `security`) are unchanged, so neither
  branch protection nor the fleet allow-list needs updating.
- `tests/test_ci_control_wiring.py`: regression guard for both drift classes — every
  `scripts/check_*.py` must be invoked by a CI job, and every job the control matrix cites
  must be defined in `ci.yml`. Includes a non-vacuity test so a parser that silently
  matches nothing cannot turn those assertions into trivial passes, and a check that the
  protected status contexts keep their exact names.
- `tests/test_ci_gates_are_real.py`: regression guard for both ways a GitHub Actions gate
  gets neutered — an exit-status swallow such as OR-true, and `continue-on-error` on a
  step or a job — plus a check that the `security` context still invokes a real bandit
  scan and a non-vacuity test so a workflow-format change cannot turn these assertions
  into trivial passes. Written before the fix and observed failing on `ci.yml:security`.

### Changed — 2026-10-03

- `.github/workflows/ci.yml`: removed the shell OR-true from the `security` job's `bandit`
  scan, so that **required status check can now fail**. It previously ended
  `bandit -r . -x .venv/ -ll || true`, discarding the scan's exit status: the job reported
  green whether or not bandit found anything. Because `security` is one of the three
  branch-protection required contexts, that green is read as assurance both by the merge
  gate and by an auditor. This is the mirror image of ADR-0004 R3's "a control without a
  failing CI job is folklore" — a job that cannot fail manufactures assurance. Verified
  safe to enable against the combined tree: the repository's own Python exits 0 with
  0 High and 0 Medium at the `-ll` threshold; Low findings stay below it. `-x .venv/` is
  left untouched — it is inert in CI, and narrowing scan scope is a separate concern from
  making the gate binding.
- `docs/adr/HERMES-0003-model-sourcing-and-mission-boundary.md` §4: now names
  `vendor-risk-check` as the enforcement locus for the null-provider invariant. The prior
  wording said only that `check_vendor_risk.py` "keeps asserting" it; because no job
  invoked that script, the assertion was not enforced. Revision History records the
  correction rather than silently rewriting the claim.
- `README.md`: supplementary control job list and the `ci.yml` structure comment updated
  from 9 jobs to 11.

### Fixed — 2026-10-03

- `docs/target-tree.md`: added `QODER.md` to the root file list and recorded the change in
  the document's Revision History. PR #21 introduced the file without reconciling this
  `Status: Accepted` tree at the same time, so the documented structure no longer matched
  `git ls-files` — the blueprint-vs-as-built drift this document exists to prevent.
- `docs/target-tree.md`: reconciled the Fleet-Standard Files table in the same `Status:
  Accepted` document. All ten rows read `Missing` while all ten files are tracked and
  present on disk, which also contradicted the document's own 2026-09-30 Revision History
  row stating "all files present". This is the opposite direction of the same defect: an
  accepted spec claiming absent files that exist is as much an audit-accuracy error as
  omitting files that exist. Statuses now read `Present`, and `.markdownlint.json` and
  `.pre-commit-config.yaml` are labelled config-only — nothing runs markdownlint, and the
  hooks are not installed — so the table no longer implies enforcement that does not exist.

### Added — 2026-10-01

- `docs/adr/HERMES-0003-model-sourcing-and-mission-boundary.md`: records that self-hosted
  inference for the Baltic (LT/LV/EE) pilot is a mission-side concern; this marketplace
  fleet must not couple to a mission inference resource (ADR-0004 R4, enforced by
  `check_deny_patterns.py`); two compliant sourcing paths are defined — a marketplace-owned
  self-hosted endpoint (assessed as infrastructure risk + model provenance, not a third-party
  DPIA) or a registered third-party provider via the full C13 DPIA. Providers stay `null`; no
  mission token is introduced.

### Changed — 2026-10-01

- `docs/adr/README.md`: added the HERMES-0003 row and restored the missing HERMES-0002 index
  entry; `docs/target-tree.md` ADR list extended to HERMES-0003

### Changed — 2026-10-01

- `evaluations/functional/README.md` and `evaluations/regression/README.md`: explicit
  populate preconditions, derivation rules, acceptance criteria, and the fact that
  populating needs no CI change (both gates discover `evaluations/**/cases.yaml`)
- `docs/tool-register.md`: both remaining observations reviewed against `policy.yaml`
  evidence and confirmed correct by design; opened one runtime follow-up on the shared
  `drift_detected` escalation pattern name declared by both audit and observability

### Fixed — 2026-10-01

- `evaluations/functional/README.md` contradicted `schemas/eval-case.schema.json` by
  describing `control` as optional; the schema requires it on every case

### Added — 2026-10-01

- `evaluations/` declarative adversarial suite: `prompt-injection` (C12), `privacy` (C11),
  `security` (C8/C9/C10) fixtures, plus `functional`/`regression` scaffolding
- `schemas/eval-case.schema.json` and `scripts/check_eval_coverage.py`
  (policy grounding + control coverage); `tests/test_eval_cases.py` (schema conformance)
- `docs/tool-register.md`: consolidated `tool_grants` -> control mapping across all 12 agents
- `docs/adr/HERMES-0002-evaluations-and-tool-register.md`
- `adversarial-evals` supplementary CI job and `make evals` target

### Fixed — 2026-10-01

- `docs/control-matrix.md`: C9/C10 no longer cite non-existent scripts
  (`check_memory_isolation.py`, `check_policy_separation.py`); enforcement repointed to
  the existing `check_deny_patterns.py`
- `docs/target-tree.md`: replaced fictional per-control workflow files with the single
  `ci.yml` job model

### Added — 2026-09-30

- Fleet-standard files: `.editorconfig`, `.markdownlint.json`, `.pre-commit-config.yaml`,
  `.gitleaksignore`, `qodana.yaml`, `.github/dependabot.yml`, `Makefile`, `pyproject.toml`
- Capability map: 12-agent roster with identity tags, dependencies, build order
- Control matrix: 17 controls mapped to enforcement mechanisms and CI jobs
- Target tree: full directory structure with agent file conventions
- Orchestrator agent scaffold (Layer 0)
- Guardrails agent scaffold (Layer 1)
- JSON Schemas for `agent.yaml` and `policy.yaml`
- Validation scripts: `validate_agents.py`, `check_deny_patterns.py`
- CI workflow with lint, test, security checks

### Governance — 2026-09-30

- Registered in fleet allow-list (`jolarca-control/repos/jolarca-hermes-agents.yml`)
- ADR prefix `HERMES-` allocated in `jolarca-docs/adr/namespace.md`
- Terraform state reconciliation complete (import + branch protection applied)
- LICENSE aligned to fleet convention (all-rights-reserved)

## [0.0.0] — 2026-09-30

- Initial repository scaffold (README, SECURITY, LICENSE, CODEOWNERS, CI)
