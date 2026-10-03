"""CI gates must be capable of failing.

ADR-0004 R3 says a control without a failing CI job is folklore. A job that
always reports success is the mirror-image failure: it manufactures assurance
while checking nothing, and because it is a *required status check* an auditor
or a branch-protection rule will read its green as proof.

Guards the two ways a GitHub Actions gate gets neutered:

  * a shell OR-true (or any spacing variant) swallowing a step's exit status
  * ``continue-on-error`` on a step or a job

The ``security`` required status check previously did the first. A non-vacuity
test asserts the parser really sees the run steps, so a workflow-format change
cannot turn these assertions into trivial passes.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

# `|| true` and spacing/casing variants swallow the real exit status.
EXIT_STATUS_SWALLOW = re.compile(r"\|\|\s*true", re.IGNORECASE)


def _workflows() -> list[tuple[str, dict]]:
    """Every workflow in .github/workflows as (filename, parsed document)."""
    loaded: list[tuple[str, dict]] = []
    for path in sorted(WORKFLOWS_DIR.glob("*.yml")):
        with path.open(encoding="utf-8") as f:
            loaded.append((path.name, yaml.safe_load(f)))
    return loaded


def _run_steps() -> list[tuple[str, str, str]]:
    """(workflow, job, script) for every run step across all workflows."""
    found: list[tuple[str, str, str]] = []
    for workflow, doc in _workflows():
        for job_name, job in (doc.get("jobs") or {}).items():
            for step in (job or {}).get("steps") or []:
                script = step.get("run")
                if isinstance(script, str):
                    found.append((workflow, job_name, script))
    return found


def test_no_run_step_swallows_its_exit_status():
    """No check may be reduced to a no-op by an OR-true."""
    offenders = [
        f"{workflow}:{job} -> {script}" for workflow, job, script in _run_steps() if EXIT_STATUS_SWALLOW.search(script)
    ]
    assert not offenders, f"run step(s) neutered by an exit-status swallow: {offenders}"


def test_no_step_or_job_declares_continue_on_error():
    """continue-on-error is the YAML spelling of the same defect."""
    offenders: list[str] = []
    for workflow, doc in _workflows():
        for job_name, job in (doc.get("jobs") or {}).items():
            if (job or {}).get("continue-on-error"):
                offenders.append(f"{workflow}:{job_name} (job)")
            for step in (job or {}).get("steps") or []:
                if step.get("continue-on-error"):
                    offenders.append(f"{workflow}:{job_name}:{step.get('name', '?')}")
    assert not offenders, f"continue-on-error declared at: {offenders}"


def test_security_check_actually_runs_bandit():
    """The protected `security` context must invoke a real scan, not an empty step."""
    scripts = [script for _, job, script in _run_steps() if job == "security"]
    assert any("bandit" in script for script in scripts), f"security job runs no bandit scan; steps were: {scripts}"


def test_workflows_are_parsed_and_non_vacuous():
    """Guard: the loader must really see ci.yml and its run steps."""
    names = [workflow for workflow, _ in _workflows()]
    assert "ci.yml" in names, f"expected ci.yml among {names}"
    steps = _run_steps()
    assert len(steps) >= 10, f"parsed only {len(steps)} run steps — workflow format may have changed"
    assert any(job == "security" for _, job, _ in steps), "no run step found under the security job"
