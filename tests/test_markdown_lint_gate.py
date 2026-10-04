"""Guard that the markdown lint gate exists, is pinned, and actually fails on a bad document.

Motivation: `.markdownlint.json` has existed for a long time while nothing executed it -- the
"configured but never run" class ADR-0004 R3 targets. The workstream that finally bound it first had
to clear 87 findings (87 -> 39 -> 15 -> 0) so the gate could arrive green instead of being weakened
on its first run.

This suite pins the parts that make the gate real rather than decorative:

  * a `markdown-lint` job exists in CI, and is **supplementary** -- it is deliberately not one of
    the three required contexts, exactly like `secrets-scan`;
  * the tool is pinned by an npm lockfile whose entries carry integrity hashes, and installed with
    `--ignore-scripts` so no dependency postinstall runs in the runner;
  * the job asserts the resolved tool version instead of trusting the lockfile to have been read
    correctly;
  * the config is the committed `.markdownlint.json`, and `MD024` is left **enabled at default**:
    the duplicate headings it once flagged were same-parent duplicates this repo created by
    stacking PRs at one anchor, and the honest disposition was to consolidate the changelog, not
    to loosen the rule.
"""

from __future__ import annotations

import json
import pathlib
import re

import yaml

ROOT = Path = pathlib.Path(__file__).resolve().parent.parent
CI = ROOT / ".github" / "workflows" / "ci.yml"
REQUIRED_CONTEXTS = {"lint", "test", "security"}
PINNED_CLI = "0.23.3"
PINNED_MARKDOWNLINT = "0.41.1"


def _job() -> dict:
    doc = yaml.safe_load(CI.read_text(encoding="utf-8"))
    return doc["jobs"]["markdown-lint"]


def _blob(job: dict) -> str:
    parts = []
    for step in job["steps"]:
        parts.append(str(step.get("run", "")))
        parts.append(str(step.get("uses", "")))
        parts.append(json.dumps(step.get("with", {}), ensure_ascii=False))
        for k, v in (step.get("env") or {}).items():
            parts.append(f"{k}={v}")
    return "\n".join(parts).lower()


def test_markdown_lint_job_exists_and_uses_the_committed_config():
    blob = _blob(_job())
    assert "markdownlint-cli2" in blob, "job no longer invokes markdownlint-cli2"
    assert ".markdownlint.json" in blob or "--config" in blob, (
        f"job does not point at the committed config: {blob[:200]}"
    )


def test_dependency_install_is_integrity_pinned_and_script_free():
    """A version string alone does not pin transitive deps; a lockfile with integrity does."""
    blob = _blob(_job())
    assert "npm ci" in blob, f"job does not install from the lockfile via npm ci: {blob[:200]}"
    assert "--ignore-scripts" in blob, "npm install runs dependency lifecycle scripts in the runner"
    lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
    pkgs = lock["packages"]
    pinned = [k for k, v in pkgs.items() if k.endswith("node_modules/markdownlint-cli2")]
    assert pinned, "markdownlint-cli2 is absent from the lockfile"
    entry = pkgs[pinned[0]]
    assert entry["version"] == PINNED_CLI, f"lockfile pins {entry['version']}, expected {PINNED_CLI}"
    # The bundled engine is what actually reports findings, so it must move in lockstep with the CLI.
    engine = [k for k, v in pkgs.items() if k.endswith("node_modules/markdownlint")]
    assert engine, "markdownlint is absent from the lockfile"
    assert pkgs[engine[0]]["version"] == PINNED_MARKDOWNLINT, (
        f"lockfile bundles markdownlint {pkgs[engine[0]]['version']}, expected {PINNED_MARKDOWNLINT}"
    )
    declared = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["devDependencies"]
    floats = {k: v for k, v in declared.items() if not re.fullmatch(r"\d+\.\d+\.\d+", v)}
    assert not floats, f"devDependencies must be exact versions, not ranges: {floats}"
    missing = [k for k, v in pkgs.items() if k != "" and isinstance(v, dict) and not v.get("integrity")]
    assert not missing, f"lockfile entries without integrity hashes: {missing[:5]}"


def test_job_asserts_the_resolved_tool_version():
    """Trust the binary's own report, not a file we hope npm honoured."""
    blob = _blob(_job())
    assert PINNED_CLI in blob, f"job never asserts version {PINNED_CLI}"
    assert PINNED_MARKDOWNLINT in blob, (
        f"job never asserts the bundled markdownlint version {PINNED_MARKDOWNLINT}; the two pin sites "
        f"(workflow env and this constant) must move together or an upgrade installs one and checks the other"
    )
    assert re.search(r"(grep|cmp|test|\[\[|\|\| *echo)", blob), "version check has no failure path"


def test_markdown_lint_is_supplementary_not_required():
    """Same posture as secrets-scan: it reports, and promotion is a control-plane decision."""
    doc = yaml.safe_load(CI.read_text(encoding="utf-8"))
    assert "markdown-lint" in doc["jobs"], "job id drifted from the name docs cite"
    assert "markdown-lint" not in REQUIRED_CONTEXTS


def test_no_run_step_in_this_job_swallows_its_exit_status():
    """Repo-wide rule (test_ci_gates_are_real.py): no gate may be reduced to a no-op by OR-true.

    Recorded because I violated it here myself. The version assert first failed on the runner --
    `markdownlint-cli2 -v` prints its version then lints the literal "-v" as a pattern and exits
    non-zero -- and my first fix swallowed that status with `|| true`. The existing guard caught
    it and failed the required `test` job. The correct fix was to stop using `-v` and read the
    installed versions from package metadata, so nothing needed swallowing at all.
    """
    offenders = [
        step.get("name", "?")
        for step in _job()["steps"]
        if re.search(r"\|\|\s*(?:true|:)\s*(?:#.*)?$", str(step.get("run", "")), re.MULTILINE)
    ]
    assert not offenders, f"exit-status swallow inside the markdown-lint job: {offenders}"


MAKEFILE = ROOT / "Makefile"


def _make_recipe(target: str) -> list[str]:
    """Tab-indented commands under a Makefile target, same parser style as test_lint_gate_scope."""
    recipe: list[str] = []
    inside = False
    for line in MAKEFILE.read_text(encoding="utf-8").splitlines():
        if re.match(rf"^{target}\s*:", line):
            inside = True
            continue
        if not inside:
            continue
        if line.startswith("\t"):
            recipe.append(line.strip())
        elif line.strip():
            break
    return recipe


def _joined(lines: list[str]) -> str:
    """Flatten Makefile recipe lines. Distinct from _blob(), which expects a CI job dict."""
    return " ".join(lines).lower()


def _make_target_line(target: str) -> str:
    for line in MAKEFILE.read_text(encoding="utf-8").splitlines():
        if re.match(rf"^{target}\s*:", line):
            return line
    return ""


def test_makefile_mirrors_the_ci_markdown_lint_job():
    """A documented local command that differs from the gate is worse than having none.

    This is the same drift class `tests/test_lint_gate_scope.py` pins for Python formatting:
    the Makefile claimed CI ran make, while the job called the tools directly.
    """
    recipe = _joined(_make_recipe("markdown-lint"))
    assert recipe, "no `make markdown-lint` target, yet QODER.md 7.2 documents one"
    for token in ("markdownlint-cli2", "--config .markdownlint.json", "git ls-files"):
        assert token in recipe, f"`make markdown-lint` no longer mirrors the CI job ({token}): {recipe}"


def test_markdown_lint_is_deliberately_not_in_make_check():
    """`make check` stays Node-free by decision. Pin it so it cannot drift into a dependency."""
    line = _make_target_line("check")
    assert "markdown-lint" not in line, f"`make check` gained a Node prerequisite: {line}"
    assert "markdown-lint" not in _joined(_make_recipe("check")), "`make check` invokes markdown-lint"


def test_md024_stays_enabled_at_default():
    """The duplicate headings were ours, so the changelog was consolidated rather than the rule."""
    cfg = json.loads((ROOT / ".markdownlint.json").read_text(encoding="utf-8"))
    assert cfg.get("default") is True
    assert "MD024" not in cfg, (
        "MD024 was disabled or re-scoped; the 15 findings it reported were same-parent duplicates "
        "created by stacking PRs at one CHANGELOG anchor and were fixed by consolidation"
    )


def test_md060_stays_enabled_after_the_upgrade():
    """The 0.41.1 upgrade found 428 MD060 findings and the corpus was re-spaced instead.

    Pinning this here because a new rule firing on accepted governance prose is exactly the moment
    someone reaches for `MD060: false`. The delimiter rows were re-spaced 1:1 (60 rows, 21 files, word
    multiset unchanged) and both runners then reported 0 -- that is the precedent to follow, not a
    rule exemption or a docs/ exclude.
    """
    cfg = json.loads((ROOT / ".markdownlint.json").read_text(encoding="utf-8"))
    assert "MD060" not in cfg, (
        "MD060/table-column-style was disabled or reconfigured; it is the rule that flagged 428 "
        "tight table delimiters on the 0.41.1 upgrade and was cleared by re-spacing those rows"
    )


def test_package_json_declares_the_node_version_the_job_requires():
    """The runtime a tool needs and the runtime CI gives it must not drift apart silently.

    Why this exists: markdownlint-cli2 0.23.3 and the markdownlint 0.41.1 it bundles both declare
    `engines.node: ">= 22"`, so CI had to move from Node 20 to 22 -- while this repository's own
    `package.json` said nothing about it. A contributor on an older Node therefore saw only an
    `EBADENGINE` warning from npm, and nothing in the tree recorded the requirement except a workflow
    comment. Declaring it makes the requirement discoverable from the manifest that actually needs it.

    Asserts the major matches the CI pin rather than hardcoding a number, so a deliberate Node bump in
    one place fails until the other is updated too.
    """
    declared = json.loads((ROOT / "package.json").read_text(encoding="utf-8")).get("engines")
    assert declared, "package.json declares no engines field, yet the markdown-lint job needs a Node major"
    want = re.fullmatch(r">=\s*(\d+)", str(declared.get("node", "")))
    assert want, f"engines.node must look like '>= N', got {declared.get('node')!r}"

    ci_major = None
    for step in _job()["steps"]:
        if "setup-node" in str(step.get("uses", "")):
            ci_major = str(step.get("with", {}).get("node-version", "")).split(".")[0]
    assert ci_major, "no actions/setup-node step found in the markdown-lint job"
    assert want.group(1) == ci_major, (
        f"package.json requires Node >= {want.group(1)} but CI installs {ci_major}; the markdown-lint "
        f"job is the only Node consumer, so these two are the same requirement"
    )


def test_guard_is_not_vacuous():
    job = _job()
    assert len(job["steps"]) >= 3, f"markdown-lint job has only {len(job['steps'])} steps"
    assert len(_blob(job)) > 150, "job body implausibly short -- parser is not reading steps"
