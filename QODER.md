# QODER.md

**Status:** Proposed
**Date:** 2026-10-03
**Applies to:** AI-assisted changes in `jolarca-hermes-agents`
**Compliance:** SOC 2 Type II · ISO 27001:2022 · GDPR Art. 32

Behavioural contract for AI-assisted work in this repository — the authoritative
source for the Hermes agent fleet of the `jolarca-dev` marketplace.

This file is a **compliance artifact**, not a style guide. The repository is a
public evidence record; every commit becomes audit evidence. An agent working
here is not merely editing files, it is producing controlled documentation.

**Tradeoff:** these rules bias toward caution over speed. For a trivial change
(a typo, one table row) use judgment. For anything touching `agents/`,
`schemas/`, `scripts/`, `docs/control-matrix.md`, or `.github/workflows/ci.yml`,
do not.

**Precedence:** explicit operator instruction > this file > tool defaults.
Where this file and the as-built repository disagree, **the repository wins**
and the disagreement is a defect to surface under §7.12 — never a licence to
silently "correct" either side.

---

## 1. Think Before Coding — Verify First

**Do not assume. Do not hide confusion. Surface tradeoffs.**

- Read a file before editing it. Read the schema before writing a document that
  must conform to it. Read `ci.yml` before claiming a job enforces anything.
- State assumptions explicitly. If uncertain, ask rather than guess.
- If more than one interpretation exists, present them. Never pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If confused, stop. Name precisely what is unclear, then ask.
- Separate **verified** (you ran it or read it) from **assumed** (you inferred
  it) in every report. Never present an assumption as evidence.

## 2. Simplicity First

**Minimum change that solves the stated problem. Nothing speculative.**

- No features beyond what was asked. No abstractions for single-use code.
- No "flexibility" or "configurability" nobody requested.
- No error handling for impossible scenarios.
- If 200 lines could be 50, rewrite it.
- The enforcement scripts use plain `pyyaml` and hand-rolled checks. Do not
  introduce a validation framework, plugin system, or new runtime dependency to
  "tidy up" that choice.
- Test: would a senior engineer call this overcomplicated? If yes, simplify.

Simplicity governs **code**. It does not license omitting a control, a test, or
a changelog entry that this repository's doctrine requires.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Do not "improve" adjacent code, comments, or formatting.
- Do not refactor what is not broken. Do not reflow a document you were asked to
  append one row to.
- Match existing style even where you would choose differently.
- If you notice unrelated dead code or drift, **mention it — do not fix it** in
  the same change.
- Remove only imports, variables, or functions that *your* change orphaned.
  Pre-existing dead code is not yours to delete unasked.
- Test: every changed line traces directly to the operator's request.

## 4. Goal-Driven Execution — Evidence Before Assertions

**Define success criteria. Loop until verified. Never claim what you did not run.**

Reframe imperatives as verifiable goals:

| Task as given | Reframe to |
|---|---|
| "Add validation" | "Write failing tests for invalid input, then make them pass" |
| "Fix the bug" | "Write a test that reproduces it, then make it pass" |
| "Refactor X" | "Prove the gate is green before and after" |
| "Add a control" | "Policy + script + failing CI job + matrix row + changelog" |
| "Document X" | "State it, then show the check that keeps it true" |

For multi-step work, state the plan with a check per step:

```text
1. [step] -> verify: [command] -> expected: [output]
2. [step] -> verify: [command] -> expected: [output]
```

A claim of "done", "passing", or "fixed" without the command and its output is
a fabricated compliance record. Do not make one.

## 5. Enforced, Not Documented

**A control without a failing CI job is folklore** (ADR-0004 R3; the third
invariant in `CONTRIBUTING.md`).

- Do not add a control to `docs/control-matrix.md` without wiring a job in
  `.github/workflows/ci.yml` that fails when the control is violated.
- Do not cite a CI job as enforcing a control without opening `ci.yml` and
  reading which script that job actually runs. Job *names* in the matrix have
  drifted from job *definitions* before.
- Prefer a machine check over a prose rule wherever feasible. Prose is not
  evidence; an exit code is.
- Never weaken a gate to make a change pass: no widening a deny-list exclusion,
  no relaxing a schema enum, no shell OR-true, no `--no-verify`.
- The mirror image is equally false: a job that exists but cannot fail is not
  enforcement either. Verify both that a job runs the check and that the check
  can actually go red.

## 6. Dual-State Honesty

**Never describe an unbuilt system in the present tense.**

This fleet is definition-only. Twelve agents carry `agent.yaml`, `policy.yaml`,
a system prompt, and tests — and `model_policy.provider` is `null` for all
twelve because model sourcing is still open (HERMES-0003 §4). HERMES-0003 §2
records that this repository is not the runtime for the Baltic pilot.

- Write "the policy declares X", not "the agent blocks X", unless a runtime
  exists and you have observed it doing so.
- Overstating enforcement to an auditor is a defect, not polish.
- Keep `designed` / `deployed` / `planned` distinctions explicit.

---

## 7. Project-Specific Rules — jolarca-hermes-agents

### 7.1 Verified snapshot

Re-verify before relying on this; it ages.

| Property | Value |
|---|---|
| Python | 3.12 (`.venv/bin/python`), `requires-python >=3.12` |
| Runtime deps | none declared; scripts import `pyyaml` only |
| Test deps | `pytest`, `pyyaml`, `jsonschema` |
| Lint | `ruff`, line-length 120, rules `E,F,W,I,UP,B,SIM` |
| Type checking | `make typecheck` is a stub — no typed code yet |
| Agents | 12, across layers 0-6 |
| Controls | 17 (C1-C17) in `docs/control-matrix.md` |
| Schemas | 4, JSON Schema Draft 2020-12, `additionalProperties: false` |
| Enforcement scripts | 17 under `scripts/` (16 `check_*.py` + `validate_agents.py`) |
| CI jobs | 15: `lint`, `test`, `security` (required) + 12 supplementary |

### 7.2 Commands

```bash
make check          # lint + validate + deny-patterns (what CI's lint job runs)
make lint           # ruff check .
make test           # pytest tests/ agents/ -v
make validate       # validate_agents.py + JSON Schema well-formedness
make evals          # check_eval_coverage.py (C8-C12 fixtures)
make deny-patterns  # scripts/check_deny_patterns.py
```

`make check` does **not** run the tests. Run `make check` and `make test` both
before claiming a change is green.

### 7.3 The deny-pattern scanner — the headline trap

`scripts/check_deny_patterns.py` enforces ADR-0004 R4: this marketplace
repository must not reference mission-platform resources. It fails on four
patterns — the mission GitHub org slug, the mission repo prefix (the letters
`jol` followed by a hyphen), and two mission local tree paths under `/opt/`.

**The trap:** the prefix pattern matches those three letters in ordinary prose,
inside backticks, and inside longer tokens. Writing them *in order to describe
the rule* trips the scanner. Only the marketplace spelling is safe: `jolarca`,
`jolarca-dev`, `agent:jolarca:*`, `/opt/jolarca/`.

Therefore:

- Never write the literal forbidden tokens into any scanned file. Refer to them
  as "the mission repo prefix", "the mission org slug", "the mission tree".
- Scanned-exempt: `*.py`; files named `policy.yaml` or `agent.yaml`; any path
  containing a `prompts/` component; and the directories `.git`, `.venv`,
  `.idea`, `__pycache__`, `node_modules`, `tests`. **Everything else is
  scanned** — every root and `docs/` Markdown file, `docs/architecture/*.mmd`,
  `evaluations/**/*.yaml`, `policies/*.md`, and this file.
- The reported scan total counts files on disk under the repo root
  (`rglob("*")`), so it exceeds the git-tracked count. Do not read it as a
  tracked-file total.
- There is no suppression mechanism. If the scan fires on your text, **rewrite
  the text**. Never propose widening an exclusion, adding a skip suffix, or
  creating a per-file exception to make a commit pass — that silently weakens
  the self-check, and it also makes the tests asserting detection pass
  vacuously.
- `policy.yaml` deny-lists and `prompts/system.md` legitimately contain the
  tokens, which is exactly why they are exempt. Do not "clean them up".
- Eval fixtures under `evaluations/` are **not** exempt. Reference the
  snake_case deny-action identifiers, never the literal tokens.

### 7.4 Fleet invariants

- Identity tag: `^agent:jolarca:[a-z][a-z0-9-]*$`, unique across the fleet,
  never reused or reassigned (HERMES-0001 §1). Enforced by
  `scripts/validate_agents.py`.
- Layer order (HERMES-0001 §2) is a build-order constraint: 0 orchestrator /
  audit / observability · 1 guardrails · 2 consent + rag · 3 content ·
  4 translation + seo + accessibility · 5 editorial · 6 website. An agent must
  not depend on a layer above its own.
- `human_gate` is one of `none`, `editorial`, `blocks_all`, `blocks_release`,
  `human_approver`. In the solo-operator era "human approval" means the operator
  reviews and merges the PR (HERMES-0001 §3). There are no teams; do not invent
  reviewers, approvers, or a review board.
- `data_classification` is one of `public`, `internal`, `confidential`,
  `restricted`. Lowering a classification is a compliance decision, not a
  refactor — ask first.
- `model_policy.provider` and `.model` stay `null` for all twelve agents until
  a HERMES-0003 sourcing path completes. Do not populate them.
- The accepted authority for ADRs and governance docs is the solo operator.

### 7.5 Schema contracts

- `agent.yaml` requires `identity_tag`, `name`, `description`, `model_policy`
  (which itself requires `provider` and `model`).
- `policy.yaml` requires `allow` and `deny`. Optional: `escalation`,
  `retention`, `budget`. `escalation.action` is one of `block`, `escalate`,
  `log_and_continue`.
- Both schemas set `additionalProperties: false`. An unknown key is a hard
  failure, not a warning. Never add a field without extending the schema and
  adding a negative test for it.
- **Action identifiers are policy-local, not control-matrix wording.** A new
  enforcement script must read the target `policy.yaml` for the real vocabulary.
  Examples: `rag` denies `unapproved_source_retrieval` and
  `cross_tenant_index_access`; `editorial` denies `approve_without_provenance`;
  `content` denies `use_unapproved_sources`; `guardrails` escalates with action
  `block`. Hardcoding matrix prose previously produced false violations in
  seven scripts.
- Convention, **not machine-enforced**: an agent's `tool_grants` in `agent.yaml`
  and `allow.actions` in `policy.yaml` enumerate the same set. Keep them in
  step — nothing in CI will tell you if you do not.

### 7.6 Where validation actually happens

`scripts/validate_agents.py` is documented as validating "against JSON Schemas".
It does not. It performs hand-rolled required-field, tag-pattern, and uniqueness
checks, and its `load_schema()` helper is defined but never called. Real Draft
2020-12 validation — positive and negative — lives in `tests/test_schemas.py`
and `tests/test_eval_cases.py`, which run in the **`test`** job, not `lint`.

Consequence: a document can pass `make check` and still violate a schema. Run
`make test` before claiming conformance. Do not fix the misleading docstring or
the dead helper as a drive-by; raise it (§7.12).

### 7.7 Tests

- Location: `tests/` for cross-agent and schema conformance;
  `agents/<name>/tests/test_<name>.py` for per-agent checks.
- House style: module docstring, `AGENT_DIR = Path(__file__).resolve().parent.parent`,
  `yaml.safe_load`, plain `assert`. Parametrised positive/negative classes with
  fixtures for schema loading in `tests/test_schemas.py`.
- `pytest` is configured with `testpaths = ["tests", "agents"]`; files match
  `test_*.py`.
- Write the failing test first. A negative test that cannot fail is not a test:
  if you add an exclusion or a deny entry, prove the check fires without it.
  Note `tests/` is deny-scan exempt, so a scanner test must write its fixture
  outside the exempt directories and with a non-exempt extension.
- Three suites guard CI integrity itself rather than agent content:
  `tests/test_ci_control_wiring.py` (every `check_*.py` is invoked; every cited
  job is defined), `tests/test_ci_gates_are_real.py` (no swallowed exit status,
  no `continue-on-error`), and `tests/test_ci_hardening.py` (actions pinned to
  full commit SHAs with version comments, workflows declare least-privilege
  `permissions`, the secret scanner is wired and licence-free). Edit `ci.yml`
  and these are the first failures to expect — they are the fix for the drift,
  not a nuisance.
- `tests/test_tool_register_consistency.py` re-derives `docs/tool-register.md` from the
  twelve `agent.yaml` files: the stated totals, each agent's grant row, the tool-index set
  in both directions, and the enumerated shared tools must all match the fleet. Edit any
  `tool_grants` list and this is where an unstale register surfaces.

### 7.8 Documentation conventions

- ADRs: prefix `HERMES-`, filename `HERMES-NNNN-short-title.md` (zero-padded to
  four digits, lowercase hyphen-separated), authored from `docs/adr/TEMPLATE.md`.
  Lifecycle `Proposed` -> `Accepted` -> `Deprecated` / `Superseded by`. Index
  every new ADR in `docs/adr/README.md` and carry the Compliance Mapping and
  Revision History tables that existing ADRs carry.
- **Never invent an ADR, control, approval, assessment, or audit record that
  does not exist.** Citing a non-existent authority in a compliance repository
  is the worst available failure mode.
- Governance docs carry `**Status:**` and `**Date:**` headers plus a Revision
  History table naming the authority.
- `CHANGELOG.md` follows Keep a Changelog under `## [Unreleased]`, using dated
  `### Added — YYYY-MM-DD` / `### Changed — YYYY-MM-DD` subsections with a
  one-paragraph rationale per entry. Add an entry for any notable change.
- Markdown: prose lines at most 120 characters (`.markdownlint.json` MD013;
  tables and code blocks are exempt). No trailing whitespace; file ends with a
  newline. Note that no CI job or installed hook currently runs markdownlint —
  treat the limit as a convention worth keeping, not a gate.
- Do not restate a fact another repository owns. `jolarca-vendor` owns the DPIA
  and vendor register behind C13; link it, do not duplicate it. Duplication is
  how the fleet's drift problem started.
- Blueprint docs (`docs/target-tree.md`) describe an *intended* tree and drift
  from the as-built state. Verify against disk before treating a difference as
  a gap to fill.

### 7.9 Failure behaviour

- A check that cannot read its input must **fail**, not return a smaller result.
- No bare `except: pass`, no silent fallback, no shell OR-true that converts a
  broken gate into a green one.
- A green gate that was never capable of going red is worse than no gate: it
  manufactures assurance. When you find one, say so explicitly.
- A required check that cannot fail is as dangerous as a control with no check
  at all. The `security` job used to end its `bandit` scan with a shell OR-true,
  discarding the scan's exit status; because `security` is a branch-protection
  required context, its green was read as assurance by the merge gate and by an
  auditor alike. Removed in PR #20 and now held shut by
  `tests/test_ci_gates_are_real.py`. If that gate ever turns red, fix the
  finding — do not reintroduce a swallow or add `continue-on-error` to clear a
  blockage.
- **Trap when reproducing that job locally.** The `-x .venv/` exclusion does not
  reliably exclude, so running the CI command verbatim in a checkout that has a
  populated `.venv` scans site-packages and reports hundreds of High findings
  from third-party code. CI has no `.venv` — `actions/checkout` fetches tracked
  files only — so its scan covers only the repository's own Python. Reproduce
  with `bandit -r scripts tests agents -ll` and **measure** the verdict; do not
  quote a stored line count, because it moves with every file added.

### 7.10 Secrets and boundaries

- Never commit credentials, tokens, API keys, PEMs, private key material, `.env`
  files, or Terraform state (`*.tfstate`, `*.tfstate.*`) — see `SECURITY.md`.
- `.pre-commit-config.yaml` declares gitleaks, `detect-private-key`,
  `check-yaml`, `check-merge-conflict`, `check-added-large-files`,
  `trailing-whitespace`, `end-of-file-fixer`, and ruff. Those hooks are **config
  only** and are not installed in this clone, so they gate nothing locally.
  Secret scanning is enforced by the CI `secrets-scan` job, which runs the
  checksum-verified gitleaks CLI over the full history. Do not substitute
  `gitleaks-action`: it requires a `GITLEAKS_LICENSE` secret for
  organisation-owned repositories and fails on every run.
- Beware the `trailing-whitespace` hook before installing it. Governance docs
  end their `**Status:**` / `**Date:**` header lines with two spaces, a
  deliberate markdown hard line break; installing the hooks strips it and
  silently restyles every such header.
- Never suggest `--no-verify`, an unsigned commit, or bypassing a hook.
- This is a **public** repository. Assume every line is read by a customer, a
  competitor, and an auditor. No infrastructure identifiers, hostnames, IP
  addresses, port numbers, or bucket names.
- Do not push, create remotes, open or merge PRs unless the operator asked.
  Those are gated operator steps.

### 7.11 Workflow

```text
VERIFY FIRST -> COMMIT -> PUSH -> REVIEW -> MERGE -> VERIFY AGAIN
```

1. **Verify first.** Establish the baseline before changing anything:
   `make check` and `make test`. Record the output. If the baseline is already
   red, stop and report it — do not build on it, and do not fix it unasked.
2. **Change.** Surgically, per §3.
3. **Verify again.** Re-run the same gates plus every script your change
   touches. A new `scripts/check_*.py` must be run standalone and shown to exit
   non-zero against a real violation *before* it is wired into CI.
4. **Commit.** `main` advances by squash merge, so the landed subject is the
   PR's first commit message with `(#N)` appended. Recent PR commits follow
   `type(scope): summary`; earlier history is plain imperative. No hook enforces
   either — prefer `type(scope): summary`, but do not describe it as enforced.
   A pathspec-isolated commit does not capture untracked new files — stage
   explicitly and confirm with `git status`.
   When two open PRs both insert at `## [Unreleased]` in `CHANGELOG.md` they
   **will** conflict even if every other file is disjoint — same anchor, both
   insert. Check `git diff --name-only --diff-filter=U` rather than assuming a
   clean merge, and resolve by re-categorising both entries rather than
   dropping one.
5. **Report.** What changed, what you ran, what it printed, what you assume,
   what you recommend. Verified and assumed kept visibly separate.

### 7.12 Drift you find in passing

Surface it; do not silently repair it, and do not silently ignore it. Known
classes, each with the check that detects it:

| Drift class | Detect with |
|---|---|
| Matrix cites a CI job that `ci.yml` does not define | `tests/test_ci_control_wiring.py` (automated); or diff job names in `docs/control-matrix.md` against `jobs:` in `ci.yml` |
| Enforcement script exists, passes, but no job runs it | `tests/test_ci_control_wiring.py` (automated); or grep each `scripts/check_*.py` basename in `ci.yml` |
| A required check cannot fail (swallowed exit status, `continue-on-error`) | `tests/test_ci_gates_are_real.py` (automated); or read each `run:` step for a swallow |
| Action ref on a mutable tag, or pinned to an abbreviated / annotated-tag SHA | `tests/test_ci_hardening.py` (automated); resolve the tag to a commit with `gh api repos/<a>/commits/<tag> --jq .sha` before pinning |
| Workflow declares no `permissions:` block | `tests/test_ci_hardening.py` (automated) |
| Job runs a different script than the matrix claims | read the job's `run:` step, not its name |
| Docstring or prose overclaims what a script checks | read the script body |
| Blueprint doc diverges from the as-built tree | diff `docs/target-tree.md` against `git ls-files` |
| ADR asserts an invariant no check enforces | grep the assertion's subject across `scripts/` and `tests/` |
| Register totals, grant rows or tool index stop matching the fleet's `tool_grants` | `tests/test_tool_register_consistency.py` (automated) |

Report these as findings with evidence and a proposed remediation, in the
response or as an issue — not as an unrequested drive-by commit, and not as a
standing deficiency list pasted into this file.

### 7.13 Definition of done

- [ ] Baseline verified green before the change, and green after.
- [ ] `make check` **and** `make test` re-run; output shown, not asserted.
- [ ] Every new or touched `scripts/check_*.py` run standalone.
- [ ] Any new control has a policy entry, an enforcement script, a CI job that
      can fail, a `docs/control-matrix.md` row, and a CHANGELOG entry.
- [ ] Any CI job cited as enforcing a control was opened and read in `ci.yml`.
- [ ] No literal forbidden token introduced into any scanned file (§7.3).
- [ ] Schemas unchanged, or changed deliberately with negative tests added.
- [ ] `model_policy.provider` still `null` unless HERMES-0003 was completed.
- [ ] New ADRs indexed in `docs/adr/README.md`; CHANGELOG entry added.
- [ ] Nothing unrelated refactored, reformatted, or "improved".
- [ ] Assumptions, drift found, and follow-ups stated explicitly in the report.

---

**These guidelines are working if:** diffs stay small and traceable; clarifying
questions arrive before implementation rather than after a mistake; claims of
success are backed by command output; controls are wired to gates that can
actually fail; unbuilt capability is described as designed rather than as
deployed; and drift found in passing is reported rather than silently repaired
or silently ignored.

---

## Revision History

| Date | Change | Authority |
|---|---|---|
| 2026-10-03 | Initial behavioural contract for AI-assisted changes | Agent (proposed, pending operator acceptance) |
| 2026-10-03 | Rebased onto merged `main` after PR #19 (eight controls wired) and PR #20 (`security` gate made binding): §7.9 open item resolved, §5 and §7.12 extended to cover gates that cannot fail, §7.11 records the squash-merge convention and the CHANGELOG conflict trap | Agent (proposed, pending operator acceptance) |
| 2026-10-03 | Updated for the CI-hardening change: job count 14 → 15 with a `secrets-scan` job, §7.10 no longer claims secret scanning is absent (and warns on the `trailing-whitespace` / hard-break conflict), §7.7 names the third guard suite, §7.12 gains unpinned-action and missing-permissions rows | Agent (proposed, PR review) |
| 2026-10-03 | §7.12 gains a tool-register consistency row and §7.7 names `tests/test_tool_register_consistency.py`, added after `docs/tool-register.md`'s totals sentence was found to contradict its own Tool index (39 claimed, 38 listed) | Agent (proposed, PR review) |
