"""CI pipeline hardening guards.

Fleet reference: `jolarca-security/tests/test_repository_controls.py`, whose
audit finding F-01 recorded three defects that were also live here:

  * action references pinned to mutable major version tags, so an upstream
    retarget silently changes what this pipeline executes;
  * abbreviated or annotated-tag SHAs, which GitHub Actions rejects outright —
    a tag can point at a tag *object*, which is not a valid pin;
  * no workflow-level `permissions:` block, leaving `GITHUB_TOKEN` at the
    organisation default rather than least privilege.

Plus the secrets control itself. `gitleaks` is declared in
`.pre-commit-config.yaml`, but the hooks are not installed and no CI job invoked
it, so the control asserted by `SECURITY.md` was folklore under ADR-0004 R3.

The scanner deliberately uses the licence-free, checksum-verified gitleaks CLI
rather than `gitleaks/gitleaks-action`, which requires a `GITLEAKS_LICENSE`
secret for organisation-owned repositories and fails on every run.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIR = ROOT / ".github" / "workflows"

# GitHub Actions resolves only a full 40-character commit SHA; abbreviated forms
# are rejected and an annotated-tag object SHA is not a commit.
FULL_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")

# Local and container references are not third-party actions.
NON_REGISTRY_PREFIXES = ("./", "docker://", "org://")


def _workflows() -> dict[str, dict]:
    return {path.name: yaml.safe_load(path.read_text(encoding="utf-8")) for path in sorted(WORKFLOW_DIR.glob("*.y*ml"))}


def _iter_uses(node) -> list[str]:
    """Collect every `uses:` action reference in a workflow document."""
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "uses" and isinstance(value, str):
                found.append(value)
            else:
                found.extend(_iter_uses(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_iter_uses(item))
    return found


def _pinnable_refs() -> list[str]:
    refs: list[str] = []
    for doc in _workflows().values():
        refs.extend(ref for ref in _iter_uses(doc) if not ref.startswith(NON_REGISTRY_PREFIXES))
    return refs


def test_action_references_are_pinned_to_full_commit_sha():
    """A mutable tag ref lets an upstream retarget change what we run."""
    offenders = [ref for ref in _pinnable_refs() if not FULL_COMMIT_SHA.match(ref.partition("@")[2])]
    assert not offenders, f"action reference(s) not pinned to a full 40-char SHA: {offenders}"


def test_every_pin_carries_a_version_comment():
    """A bare SHA is unauditable; the fleet convention annotates the resolved version."""
    missing = []
    for name in _workflows():
        for line in (WORKFLOW_DIR / name).read_text(encoding="utf-8").splitlines():
            if "uses: " not in line:
                continue
            revision = line.partition("@")[2].split("#")[0].strip()
            if FULL_COMMIT_SHA.match(revision) and "#" not in line:
                missing.append(f"{name}: {line.strip()}")
    assert not missing, f"SHA pin(s) without a version comment: {missing}"


def test_workflows_declare_least_privilege_permissions():
    """Without an explicit block the token keeps the organisation default."""
    for name, doc in _workflows().items():
        permissions = doc.get("permissions")
        assert isinstance(permissions, dict) and permissions, f"{name} declares no permissions"
        for scope, level in permissions.items():
            assert level == "read", f"{name} grants {scope}: {level}; write needs justification"


def test_secret_scan_job_is_enforced_by_ci():
    """Gitleaks must actually run somewhere; declared hooks are not installed here."""
    jobs = _workflows()["ci.yml"]["jobs"]
    scanners = [name for name, job in jobs.items() if "gitleaks" in yaml.safe_dump(job).lower()]
    assert scanners, "no CI job invokes gitleaks — SECURITY.md's control is unenforced"


def test_secret_scan_is_license_free_and_checksum_verified():
    """Reference: jolarca-security F-01. The action needs GITLEAKS_LICENSE."""
    text = (WORKFLOW_DIR / "ci.yml").read_text(encoding="utf-8")
    for ref in _iter_uses(_workflows()["ci.yml"]):
        assert "gitleaks-action" not in ref, f"'{ref}' requires GITLEAKS_LICENSE for organisation repositories"
    assert "sha256sum -c" in text, "gitleaks download is not checksum verified"
    assert "--redact" in text, "gitleaks must redact findings so secrets never reach CI logs"
    assert "fetch-depth: 0" in text, "gitleaks must scan full history, not only HEAD"


def test_guard_is_not_vacuous():
    """The parser must really see the action refs, or the pins above pass trivially."""
    refs = _pinnable_refs()
    assert len(refs) >= 28, f"parsed only {len(refs)} action refs — workflow format may have changed"
    assert all("@" in ref for ref in refs), "an action reference carries no revision"
