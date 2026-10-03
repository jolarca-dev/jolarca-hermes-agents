"""CI-to-control wiring tests.

Asserts the two drift classes that previously left controls as folklore
(ADR-0004 R3: a control without a failing CI job is folklore):

  * an enforcement script under ``scripts/`` that no CI job invokes
  * a CI job that ``docs/control-matrix.md`` cites but ``ci.yml`` does not define

Both are documentation-accuracy defects in a public compliance artifact, so the
guard includes a non-vacuity test: a parser that silently matches nothing would
otherwise turn these assertions into trivial passes.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CI_FILE = REPO_ROOT / ".github" / "workflows" / "ci.yml"
SCRIPTS_DIR = REPO_ROOT / "scripts"
CONTROL_MATRIX = REPO_ROOT / "docs" / "control-matrix.md"

# The three branch-protection required status checks, referenced verbatim.
REQUIRED_CHECKS = {"lint", "test", "security"}


def _defined_jobs() -> set[str]:
    """Job ids actually defined under ``jobs:`` in ci.yml."""
    with CI_FILE.open(encoding="utf-8") as f:
        return set(yaml.safe_load(f)["jobs"])


def _check_scripts() -> list[Path]:
    """Enforcement scripts, excluding validate_agents.py which is not a check_*."""
    return sorted(SCRIPTS_DIR.glob("check_*.py"))


def _cited_jobs() -> set[str]:
    """Job names cited by the control matrix's two job-bearing columns.

    The Controls table carries a C-id in its first column and job names in its
    last; the CI Job Mapping table carries the job name in its first column.
    Matching on ``C<digits>`` alone keeps SOC 2 / ISO codes out of the result.
    """
    cited: set[str] = set()
    for line in CONTROL_MATRIX.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        candidates: list[str] = []
        if re.fullmatch(r"C\d+", cells[0]):
            candidates.append(cells[-1])
        elif cells[0].startswith("`"):
            candidates.append(cells[0])
        for cell in candidates:
            cited.update(re.findall(r"`([a-z0-9-]+)`", cell))
    return cited


def test_every_check_script_is_wired_into_ci():
    """Each scripts/check_*.py must be invoked by at least one CI job."""
    ci_text = CI_FILE.read_text(encoding="utf-8")
    unwired = [script.name for script in _check_scripts() if script.name not in ci_text]
    assert not unwired, f"enforcement script(s) invoked by no CI job: {unwired}"


def test_control_matrix_cites_only_defined_jobs():
    """Every CI job the control matrix names must exist in ci.yml."""
    phantom = sorted(_cited_jobs() - _defined_jobs())
    assert not phantom, f"control-matrix cites undefined CI job(s): {phantom}"


def test_parser_is_not_vacuous():
    """Guard: the matrix parser must really find job names, or the tests above pass trivially."""
    cited = _cited_jobs()
    assert len(cited) >= 9, f"parser found only {sorted(cited)} — matrix format may have changed"
    assert REQUIRED_CHECKS.isdisjoint(cited), "required checks must not be parsed as control jobs"


def test_required_status_checks_still_defined():
    """The protected contexts keep their exact names; renaming them breaks branch protection."""
    missing = sorted(REQUIRED_CHECKS - _defined_jobs())
    assert not missing, f"required status check(s) missing from ci.yml: {missing}"


def test_scripts_exist_to_wire():
    """Guard: the fleet must still ship the 16 control scripts this suite reasons about."""
    assert len(_check_scripts()) == 16
