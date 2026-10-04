# Changelog

All notable changes to `jolarca-hermes-agents` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `package.json` declares `engines.node: ">=22"`, and `tests/test_markdown_lint_gate.py` now asserts that
  declaration **matches the CI `node-version`** instead of hardcoding a number, so the runtime a contributor
  installs and the runtime the gate runs in cannot drift apart unnoticed. The requirement existed only as a
  workflow comment and as an `EBADENGINE` warning on any machine below 22 -- including this one, measured at
  Node **20.20.2**, while CI installed **22**. Guard written first and seen red: `1 failed, 10 passed` with
  the failure being the absent `engines` field. Mutation-proved after: setting `engines.node` to `>=20`
  fails against CI's 22, and deleting the field fails again; each restore byte-identical.
  `CONTRIBUTING.md` gained a "Markdown linting" section (Node 22, the `npm ci` line, and why `make check`
  still stays npm-free); `QODER.md` §7.2 now names the Node major in the command list. Verified the lockfile
  stays in sync: npm records only `name`/`version`/`devDependencies` in the lock root, and `npm ci --dry-run`
  after the edit still exits 0 rather than reporting `package.json` and `package-lock.json` out of sync.

- `tests/test_precommit_hook_safety.py`, plus the mitigation it pins: `.pre-commit-config.yaml`'s
  `trailing-whitespace` hook now carries `args: [--markdown-linebreak-ext=md]`. The config had declared
  the hook with no arguments while three `Status: Accepted` governance docs open their metadata headers
  with two-space markdown hard breaks -- **5 lines**, in `docs/capability-map.md:3-4`,
  `docs/control-matrix.md:3-4`, `docs/target-tree.md:3`. Installing the hook and committing any edit to
  those files would have stripped them, and because the *next* metadata line has no hard break of its
  own, `**Status:** Accepted **Date:** 2026-09-30 **ADR prefix:** HERMES-` collapses into one rendered
  paragraph. The damage was latent, not theoretical: nothing installed the hook, so nothing exercised it.

  The guard requires the argument **and forbids replacing it with a `docs/` exclude** -- an exclude would
  delete real trailing-whitespace coverage across the whole governance corpus to protect five lines. It
  also fails if the hard-break construct disappears, so the mitigation cannot quietly become decorative,
  and it asserts every declared hook `rev` is an exact version rather than a branch.

  Measured, not assumed (`pre-commit 4.6.2`, hook installed in this clone, then probed):
  `pre-commit run trailing-whitespace --all-files` **Passed and modified nothing** -- the 5 breaks
  survived at 2/2/1. On a probe file the hook exited 1 and fixed it: two-space breaks preserved, three
  spaces normalised to two, single spaces and tabs still stripped. So the mitigation protects the
  construct without exempting anything.

  Documentation gap closed too: `CONTRIBUTING.md` never mentioned pre-commit at all, so installation was
  undiscoverable. It now carries the install and manual-run commands and states that **no CI job runs
  pre-commit** -- the binding gates remain the three required contexts plus the supplementary jobs.
  `QODER.md` §7.10 and `docs/target-tree.md` said the hooks were "config only / not installed"; hooks
  are per clone, so both now say that precisely instead of describing one working copy as fact.

- `Makefile`: a `markdown-lint` target, and `QODER.md` §7.2 now documents it. Until this change the
  docs gate existed in CI but **nowhere in the contract's command list** -- "markdown" appeared nowhere
  in §7.2 -- so a contributor obeying the file had no way to run the gate locally and met it cold in a
  PR. The recipe mirrors the CI job exactly (`git ls-files` scope, `--config .markdownlint.json`, the
  lockfile-installed binary) and fails loudly when the tool is absent instead of skipping.

  **Deliberately excluded from `make check`.** The pre-merge Python loop must not acquire an npm
  dependency. Both decisions are now pinned by `tests/test_markdown_lint_gate.py` (two new tests) so
  neither can drift: someone adding `markdown-lint` to `check`, or quietly diverging the local recipe
  from the CI job, gets a failing build. Measured rather than asserted -- with `node_modules` moved
  out of the tree, `make check` exits **0** while `make markdown-lint` exits **2** with an install
  hint; with the tool present the target lints 49 files at 0 errors.

- `.github/dependabot.yml`: an `npm` ecosystem for the root directory, so the
  `package.json`/`package-lock.json` pair introduced by the markdownlint gate is actually monitored.
  **This closed a gap I created myself**: PR #37 pinned markdownlint-cli2 and ~80 transitive packages
  with integrity hashes while dependabot declared only `github-actions` and `pip`, leaving 81 packages
  ageing with nothing watching them in a repo whose doctrine is that nothing may be pinned and left
  unmonitored. Measured before fixing: ecosystems were exactly those two.

  `tests/test_dependabot_coverage.py` holds the parity **bidirectionally** -- every manifest in the
  tree needs an ecosystem, and no ecosystem may point at a directory holding no such manifest -- so
  the gap cannot recur when a dependency is added later, and a removed manifest cannot leave a dead
  entry behind. Also recorded here: repo-level `vulnerability-alerts` and `automated-security-fixes`
  both answered the API's success status, so Dependabot security updates are possible here, not only
  version bumps.

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

- `tests/test_tool_register_consistency.py`: re-derives every figure `docs/tool-register.md`
  states from the twelve `agent.yaml` files — the totals sentence (grants / agents /
  distinct), each agent's grant row, the Tool index set in **both** directions, and the
  enumerated shared tools. Closes the `QODER.md` drift class "an agent grants a tool the
  register does not list", which previously had no automated check. Includes a non-vacuity
  test so a parser that stops matching fails loudly rather than passing trivially.
  Written first and observed failing on precisely one assertion
  (`register claims 39 distinct tools; the fleet grants 38`) with the other four already
  green — which is what proved the defect was a single prose figure, not a broken register.

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

- `docs/adr/HERMES-0003-model-sourcing-and-mission-boundary.md`: records that self-hosted
  inference for the Baltic (LT/LV/EE) pilot is a mission-side concern; this marketplace
  fleet must not couple to a mission inference resource (ADR-0004 R4, enforced by
  `check_deny_patterns.py`); two compliant sourcing paths are defined — a marketplace-owned
  self-hosted endpoint (assessed as infrastructure risk + model provenance, not a third-party
  DPIA) or a registered third-party provider via the full C13 DPIA. Providers stay `null`; no
  mission token is introduced.

- `evaluations/` declarative adversarial suite: `prompt-injection` (C12), `privacy` (C11),
  `security` (C8/C9/C10) fixtures, plus `functional`/`regression` scaffolding
- `schemas/eval-case.schema.json` and `scripts/check_eval_coverage.py`
  (policy grounding + control coverage); `tests/test_eval_cases.py` (schema conformance)
- `docs/tool-register.md`: consolidated `tool_grants` -> control mapping across all 12 agents
- `docs/adr/HERMES-0002-evaluations-and-tool-register.md`
- `adversarial-evals` supplementary CI job and `make evals` target

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

### Changed

- **markdownlint re-pinned: `markdownlint-cli2` 0.17.2 to 0.23.3 (bundling markdownlint 0.37.4 to 0.41.1),
  and CI `node-version` 20 to 22.** Step two of the agreed measure-then-bind sequence: the 428 `MD060`
  findings the candidate produced were cleared by the delimiter-spacing pass *before* the pin moved, so this
  lands green instead of being weakened on its landing day. Supersedes dependabot's #40, proven to carry the
  identical version transition (dependency `0.23.3`, CLI `0.23.3`, engine `0.41.1`, lockfile 1385 lines both
  sides, and #40 touches only the two package files). #40 is closed rather than merged because it sits behind
  main and cannot see the delimiter fix it now depends on.

  Node moved because both packages declare `engines.node: ">= 22"`; `npm install` under the repository's
  local Node 20 emitted `EBADENGINE` rather than hiding it. `markdown-lint` is the workflow's only Node
  consumer, so no other gate is affected, and the verdict still comes from the integrity-pinned CLI asserted
  by exact string rather than from the runtime.

  Re-measured on the new lock: **88 entries, 0 without an integrity hash, 0 declaring install scripts** --
  `npm ci --ignore-scripts` still skips nothing legitimate. `npm install` rewrote the dependency to a caret
  range; that was reverted to exact `0.23.3`, because a range silently widens what the lockfile is trusted to
  reproduce.

  The guard was tightened, not merely re-numbered. `tests/test_markdown_lint_gate.py` now also asserts the
  **bundled engine** version (the two pin sites must move together, or an upgrade installs one and checks the
  other), forbids a floating range in `devDependencies`, and pins `MD060` at default so the next new rule
  cannot be answered by disabling it. Mutation-proved, each restored byte-identically: dependency widened to
  a range = 1 failed; workflow engine constant left at the old value = 1 failed; `MD060: false` = 1 failed.
  The coupling was demonstrated *before* the fix as well: bumping the lock while the constant still read
  `0.17.2` failed `test_dependency_install_is_integrity_pinned_and_script_free` (1 failed, 8 passed), which is
  precisely the drift that guard exists to catch.

  Verified with the real tool after `npm ci`: 49 tracked files, **0 issues**. `make check` rc 0, 172 tests
  (was 171), deny-scan no violations. `QODER.md` §7.8 needed no edit -- it deliberately names no version
  numbers. Older entries here that state "Node is pinned to major 20" or cite `0.17.2 (0.37.4)` are left as
  written: they record what shipped on that date, and this entry supersedes them.

- Table delimiter rows are now spaced to match their header rows (`|---|---|` → `| --- | --- |`) across
  the corpus: **60 rows in 21 files**, `+60/−60` exactly. This is step one of upgrading the pinned
  markdownlint, measured before binding. `MD060/table-column-style` does not exist in the pinned
  **markdownlint 0.37.4** but ships in **0.41.1** (dependabot's #40), where its `style: "any"` default
  requires each table's column pipes to be internally consistent -- this corpus writes spaced header rows
  over tight delimiter rows, so upgrading produced **428 findings in 21 files** on a doc set the current
  gate reports clean. Re-spacing the delimiter rows clears it without weakening anything: verified
  **428 → 0** with the 0.41.1 runner and still **0** with the pinned 0.17.2, so this lands green under the
  gate as it stands today. Structural proofs, each stated against the measurement it actually came from: the
  spacing pass alone replaced **60 delimiter rows 1:1** with files 49, lines 4277 and the word **multiset**
  identical before and after, only `.md` files touched, and the 5 governance-header hard breaks unchanged.
  The commit is wider than the pass because it also carries this entry, two revision rows and the new
  structural guard: `+148/−60` over 23 files, markdown words 27658 → 28091, and all 60 removed lines are
  delimiter rows -- zero non-delimiter lines removed. No rule was disabled and no baseline
  added -- MD060's configuration surface (`aligned_delimiter`,
  `style: aligned|any|compact|tight`) was read from the installed package rather than recalled. The upgrade
  itself follows separately: package files, `PINNED_CLI`/`PINNED_MARKDOWNLINT`, and CI `node-version`, which
  0.41.1 requires at **>= 22** while we pin **20**.

  **Self-inflicted, caught before push, and now guarded:** the first revision row written into `QODER.md`
  put literal pipe-dashes inside a table cell, producing a 7-cell row in a 3-cell table -- `MD056` plus
  seven `MD060` findings -- and it made the **currently pinned** linter fail as well
  (`make markdown-lint` exit 2). The required contexts would not have caught it, because no test asserted
  the shape of the revision tables. The row was reworded without pipes, and
  `tests/test_markdown_table_shape.py` now asserts that every row of the `QODER.md` and
  `docs/target-tree.md` revision tables has exactly three cells.

- **markdownlint is now a CI gate.** `.github/workflows/ci.yml` gained a `markdown-lint` job running
  `markdownlint-cli2` against the committed `.markdownlint.json` over `git ls-files '*.md'`. It is
  **supplementary**, the same posture as `secrets-scan`: it reports, and promotion to a required
  context is a control-plane decision, not something this repository can grant itself.

  **Pinning.** An exact version of `markdownlint-cli2` does not pin its ~80 transitive dependencies,
  which float on semver ranges, so the repo now carries `package.json` + `package-lock.json`
  (dev-only; nothing here is installed at build time). Measured on that lock: 81 packages, **80 of 80
  non-root entries carry a sha512 integrity hash**, and **zero declare install scripts** -- which is
  why `npm ci --ignore-scripts` skips nothing legitimate while guaranteeing no dependency lifecycle
  code executes in the runner. The job then reads the **installed** versions from each package's own
  `package.json` under `node_modules` and fails on any mismatch against
  `markdownlint-cli2 v0.17.2 (markdownlint v0.37.4)`. It deliberately does **not** shell out to
  `markdownlint-cli2 -v`: that binary prints its version and then treats `-v` as a file pattern, so it
  exits non-zero, and my first attempt to work around that used an OR-true swallow -- which
  `tests/test_ci_gates_are_real.py` correctly rejects, failing the required `test` job. The rule was
  right and the workaround was dropped; the job now has nothing to swallow. A local guard in
  `tests/test_markdown_lint_gate.py` polices the same rule inside this job so it cannot come back.
  Node is pinned to major `20` via SHA-pinned `actions/setup-node`; the residual float inside 20.x is
  accepted because Node does not decide the verdict. `package-lock.json` is a generated file added to
  a repository with no runtime dependencies -- worth flagging for review on exactly that basis.

  **MD024 disposition, honestly.** The rule stays **enabled at default**; nothing was loosened. The
  15 findings were same-parent duplicates this repo manufactured, and the fix was the heading
  consolidation above. The root cause was also still live in `QODER.md`, which instructed
  contributors to write dated `### Added — YYYY-MM-DD` subsections under `## [Unreleased]` -- i.e. the
  contract told every PR to regrow exactly what the new gate rejects. Binding MD024 without correcting
  that instruction would have made the next compliant contributor fail CI, so §7.8 now mandates one
  undated heading per category. `docs/target-tree.md` and `QODER.md` §7.8 both previously stated that
  **nothing runs markdownlint**; those claims are now false and were updated in the same change.

- `CHANGELOG.md`: consolidated `## [Unreleased]` from **25 dated sub-headings into one heading per
  category** (`Added`, `Changed`, `Fixed`, plus `Governance` kept as its own). This is what actually
  cleared the last 15 `MD024` findings: same-parent duplicates produced by every PR in this
  workstream inserting its own dated block at the same anchor.

  Preservation was proved against a snapshot taken before the move and checked independently of the
  transform: all **59 bullet lines identical** (zero lost, zero added). `Governance` was **not**
  folded into `Changed` — it is a real category used once, and flattening a category to satisfy a
  linter is editing documentation down to make a gate pass, the move this repository forbids. Date
  suffixes left the headings because chronology survives in ordering, in the PR numbers cited inside
  each entry, and in git history.

- Ran `markdownlint-cli2 --fix` over the tracked markdown set, clearing 46 findings across 13
  files: `MD032/blanks-around-lists` (27), `MD022/blanks-around-headings` (19) and
  `MD037/no-space-in-emphasis` (1). Repo-wide lint count 87 → 39.

  Step 1 of the agreed measure-then-bind plan: **format first, bind later**, so the eventual gate
  arrives green instead of being weakened on the day it ships. No gate was added here, so nothing
  can fail on arrival and nothing was edited down to satisfy a tool.

  The change is whitespace plus one broken emphasis marker, proved by classifying every diff line
  rather than by trusting the lint count: **35 blank lines added, 0 removed, exactly one
  non-blank pair** — `policies/data-processing-policy.md` line 72 read
  `** editorial gate required:**`, where the space after `**` stopped the bold marker from ever
  closing, in a GDPR/data-classification policy document. Verified independently of the linter by
  comparing per-file word, heading, list-item, fence and table-row counts before and after: all
  unchanged. Re-running `--fix` immediately after produces zero further changes, so the fixer is
  idempotent.

  Excluded from that pass and completed afterwards: the 17 `MD013` prose wraps (governance text, so
  wrapped line by line with a word-multiset proof), the 7 `MD040` unlabelled fences (the first
  labeller also relabelled **closing** fences, and a closing fence cannot carry an info string, so
  the final pass tracks open/close state), and this file's 15 `MD024` duplicate-heading findings.

  The wording originally written here attributed `MD024` partly to the Keep a Changelog format,
  implying `siblings_only: true` would resolve it. **Measured, that diagnosis was wrong:** all 21
  dated sub-headings sit under the single parent `## [Unreleased]`, so that option would have
  cleared zero findings. They are same-parent duplicates this workstream created by inserting its
  own dated block at the same anchor in every PR from #22 to #35. The fix was consolidating the
  headings, not loosening the config.

- `QODER.md` §7.10 corrected: it said secret scanning "**is enforced by** the CI
  `secrets-scan` job." The job does run on every pull request and push and does fail on a
  hit, but it is **not** one of the three required status checks. Verified against the live
  API: `strict=true`, `contexts=lint,test,security`, `enforce_admins=true` — so a leaking PR
  is marked red yet remains mergeable. The wording now states exactly that, and warns against
  describing it as merge-blocking. `README.md` was already correct (it lists the three required
  checks and files `secrets-scan` under supplementary), so only the contract file drifted.
- Attempted promotion of `secrets-scan` to a required context, and found it cannot be done
  from here; recorded rather than worked around. The required contexts are declared in
  `jolarca-control/repos/jolarca-hermes-agents.yml`, but that Terraform root holds **no state**
  (`terraform state list` exits 1: "Terraform has not yet made changes to your existing
  configuration or state"), `make apply` is refused by design, `AGENTS.md` §5 forbids an agent
  both `terraform apply` from that root and any `gh api -X PATCH` of branch protection, and §8
  records that D-01/D-02/D-18/D-20/D-33 block the first apply and that no targeted-apply
  mechanism exists. Two further defects surfaced while verifying: `branch-protection.tf`
  lines 18-20 still assert `enable_branch_protection = false` while `terraform.tfvars:46` sets
  it `true` (stale rationale in a high-blast-radius file), and the control file declares
  `compliance.required_gates.secret_scan: true` while no server-side rule requires that check —
  the "never describe a control as enforced when it is configured-but-inert" rule its own §6
  states. Left as an operator decision; nothing in the sibling repo was modified.

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

- `Makefile`: two comments claimed CI invokes make — the header ("CI job `lint` runs
  `make check`") and the `check` target's help text ("Full pre-merge check (CI runs this)").
  **Both false**: the job invokes `ruff check .`, `python scripts/validate_agents.py` and
  `python scripts/check_deny_patterns.py` as three explicit steps and never calls make. The
  claim was not cosmetic: had it been true, adding the formatting gate to the Makefile alone
  would have sufficed; because it is false, a Makefile-only change binds nothing in CI. That
  is precisely the "control that exists but runs nowhere" defect ADR-0004 R3 targets, so the
  gate is wired in both places and both comments rewritten. `QODER.md` §7.1 and §7.2 corrected
  to match, and §7.12 gains the corresponding drift row.

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

- `docs/adr/README.md`: added the HERMES-0003 row and restored the missing HERMES-0002 index
  entry; `docs/target-tree.md` ADR list extended to HERMES-0003

- `evaluations/functional/README.md` and `evaluations/regression/README.md`: explicit
  populate preconditions, derivation rules, acceptance criteria, and the fact that
  populating needs no CI change (both gates discover `evaluations/**/cases.yaml`)
- `docs/tool-register.md`: both remaining observations reviewed against `policy.yaml`
  evidence and confirmed correct by design; opened one runtime follow-up on the shared
  `drift_detected` escalation pattern name declared by both audit and observability

### Fixed

- `QODER.md` §7.5 and §7.6 both described the compliance spine as it stood **before** work already on
  `main`, which is the direction of staleness that makes a contract actively misleading:
  - §7.5 asserted that `tool_grants` vs `allow.actions` parity was "Convention, **not
    machine-enforced**" and "nothing in CI will tell you if you do not." False since PR #29: the
    required `test` job runs `tests/test_tool_grant_policy_parity.py`. Rewritten to state the real
    invariant -- a **one-way subset**, because measured, only `orchestrator` has the two sets equal and
    asserting equality would demand a fiction of the other eleven -- and to keep the `allow.actions`
    top-level nesting gotcha that previously cost me a vacuous pass.
  - §7.6 described `validate_agents.py` as carrying a misleading "against JSON Schemas" docstring with
    a dead `load_schema()` helper, and warned not to fix them as a drive-by. PR #24 already corrected
    the docstring and deleted the helper; `load_schema` no longer exists in the file. The section now
    states what the script actually checks and marks the old warning obsolete.

  Found while doing the §7.2 work above. Disclosed here and described as its own logical change rather
  than repaired silently, per §7.12; it ships in the same commit as the §7.2 work, not as a hidden
  hunk. Also corrected `docs/target-tree.md`'s Makefile row, which listed 6 of 11
  targets -- a row my own change would otherwise have made staler. (§7.7's suite count was already
  brought current in the dependabot PR #38, so no change was needed there.)

- `QODER.md` Revision History: the row added for PR #32 was missing its third cell. The table
  is `| Date | Change | Authority |`, but that row ended immediately after the change text, so
  the attribution was silently absent. Introduced by the script that appended the row, not by
  hand.

  Found only by `markdownlint-cli2` (`MD056/table-column-count`) while measuring the docs ahead
  of binding a markdown lint gate — which is the point worth recording: nothing in `make check`,
  `ruff check`, `ruff format --check`, the deny-pattern scan or the 149 tests can observe a
  malformed markdown table. A governance document can lose an attribution row and every
  existing gate stays green.

  Manual one-line fix, verified with the real linter: all nine revision rows now carry three
  cells, and the repo-wide count drops 87 → 86 with MD056 gone. The 15 `MD024` duplicates in this
  file's own `[Unreleased]` block were later cleared by heading consolidation — they were all
  same-parent duplicates created by stacking PRs in one workstream, **not** the Keep a Changelog
  format itself, which is what an earlier sentence in this entry incorrectly claimed until it was
  measured (see the `MD024` correction under Changed).

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

- `evaluations/functional/README.md` contradicted `schemas/eval-case.schema.json` by
  describing `control` as optional; the schema requires it on every case

- `docs/control-matrix.md`: C9/C10 no longer cite non-existent scripts
  (`check_memory_isolation.py`, `check_policy_separation.py`); enforcement repointed to
  the existing `check_deny_patterns.py`
- `docs/target-tree.md`: replaced fictional per-control workflow files with the single
  `ci.yml` job model

### Governance

- Registered in fleet allow-list (`jolarca-control/repos/jolarca-hermes-agents.yml`)
- ADR prefix `HERMES-` allocated in `jolarca-docs/adr/namespace.md`
- Terraform state reconciliation complete (import + branch protection applied)
- LICENSE aligned to fleet convention (all-rights-reserved)

## [0.0.0] — 2026-09-30

- Initial repository scaffold (README, SECURITY, LICENSE, CODEOWNERS, CI)
