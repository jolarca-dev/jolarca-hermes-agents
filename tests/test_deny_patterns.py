"""Tests for the deny-pattern scanner (ADR-0004 R4)."""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_deny_patterns.py"


def test_deny_patterns_passes_on_clean_repo():
    """The repo itself should pass the deny-pattern scan."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"check_deny_patterns.py failed:\n{result.stdout}\n{result.stderr}"


def test_deny_patterns_catches_jol_prefix():
    """The scanner catches jol-* references (but not jolarca*)."""
    test_file = REPO_ROOT / "_test_mission_ref.md"
    try:
        test_file.write_text("# Reference to jol-infrastructure\n")
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 1
        assert "jol-" in result.stdout
    finally:
        test_file.unlink(missing_ok=True)


def test_deny_patterns_catches_journeyoflife_org():
    """The scanner catches journeyoflife-org references."""
    test_file = REPO_ROOT / "_test_mission_org.md"
    try:
        test_file.write_text("# Reference to journeyoflife-org\n")
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 1
        assert "journeyoflife-org" in result.stdout
    finally:
        test_file.unlink(missing_ok=True)


def test_deny_patterns_allows_jolarca():
    """The scanner does NOT flag jolarca* references."""
    test_file = REPO_ROOT / "_test_jolarca_ok.md"
    try:
        test_file.write_text("# Reference to jolarca-control is fine\n")
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0
    finally:
        test_file.unlink(missing_ok=True)
