"""Tests for the agent validator."""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "validate_agents.py"


def test_validate_agents_passes():
    """All current agents pass validation."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"validate_agents.py failed:\n{result.stdout}\n{result.stderr}"
    )
    assert "PASSED" in result.stdout
    assert "12 agent(s)" in result.stdout
