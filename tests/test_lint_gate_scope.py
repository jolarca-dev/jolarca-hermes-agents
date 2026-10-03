"""Guard that the required `lint` check actually enforces Python formatting.

The finding that motivated this suite: `Makefile` carried the comment "CI job
`lint` runs `make check`", but `ci.yml`'s `lint` job never calls make — it runs
`ruff check .`, `validate_agents.py` and `check_deny_patterns.py` as three explicit
steps. Adding a formatting assertion to the Makefile alone would therefore not bind
in CI at all: a control that exists but runs nowhere, which is the defect
ADR-0004 R3 and `QODER.md` §5 exist to prevent.

So both halves are pinned here. If someone drops the format check from either the
Makefile or the CI job, or reverts the job to invoking make, these tests fail.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MAKEFILE = ROOT / "Makefile"
CI_FILE = ROOT / ".github" / "workflows" / "ci.yml"


def _lint_recipe() -> list[str]:
    """Tab-indented commands under the Makefile's `lint` target."""
    recipe: list[str] = []
    inside = False
    for line in MAKEFILE.read_text(encoding="utf-8").splitlines():
        if re.match(r"^lint\s*:", line):
            inside = True
            continue
        if not inside:
            continue
        if line.startswith("\t"):
            recipe.append(line.strip())
        elif line.strip():
            break
    return recipe


def _ci_lint_runs() -> list[str]:
    """Every `run:` script in ci.yml's required `lint` job."""
    doc = yaml.safe_load(CI_FILE.read_text(encoding="utf-8"))
    return [step["run"] for step in doc["jobs"]["lint"]["steps"] if step.get("run")]


def _blob(commands: list[str]) -> str:
    return " ".join(commands)


def test_makefile_lint_target_verifies_formatting():
    recipe = _blob(_lint_recipe())
    assert "RUFF" in recipe and "check" in recipe, f"`make lint` no longer runs ruff check: {recipe}"
    assert "format" in recipe and "--check" in recipe, f"`make lint` does not verify formatting: {recipe}"


def test_ci_lint_job_verifies_formatting():
    """The Makefile is not enough: CI's lint job calls the tools directly."""
    runs = _blob(_ci_lint_runs())
    assert "ruff check" in runs, f"required `lint` job no longer runs ruff check: {runs}"
    assert "format" in runs and "--check" in runs, f"required `lint` job does not enforce formatting: {runs}"


def test_ci_lint_job_still_enforces_the_other_two_controls():
    """Formatting must not crowd out validation or the deny-pattern scan."""
    runs = _blob(_ci_lint_runs())
    for script in ("validate_agents.py", "check_deny_patterns.py"):
        assert script in runs, f"required `lint` job no longer runs {script}: {runs}"


def test_guard_is_not_vacuous():
    """A parser that finds nothing would make every assertion above pass trivially."""
    assert len(_lint_recipe()) >= 2, f"parsed only {len(_lint_recipe())} `lint` commands"
    runs = _ci_lint_runs()
    assert len(runs) >= 3, f"parsed only {len(runs)} run steps in the lint job"
