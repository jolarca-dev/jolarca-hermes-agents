"""Guard that every dependency manifest in the tree is monitored by a dependabot ecosystem.

Motivation is self-inflicted and specific: this repo added `package.json` + `package-lock.json` to
pin markdownlint-cli2 with integrity hashes (PR #37), while `.github/dependabot.yml` declared only
`github-actions` and `pip`. Result: 81 npm packages pinned, monitored by nothing, quietly ageing in a
repository whose doctrine is that nothing may be pinned and left unmonitored. A pin without
monitoring is how a "no unpinned tools" rule ends up with a stale pin that still reads compliant.

The invariant is **bidirectional**:
  * every manifest that exists must have an ecosystem covering its directory;
  * every ecosystem entry must point at a directory that actually holds such a manifest
    (`github-actions` is exempt -- it monitors workflow refs, not a manifest file).
A one-way check would let a removed manifest leave a dead entry behind.
"""

from __future__ import annotations

import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".github" / "dependabot.yml"

#: manifest filename -> dependabot ecosystem id
MANIFESTS = {
    "package.json": "npm",
    "package-lock.json": "npm",
    "yarn.lock": "npm",
    "pyproject.toml": "pip",
    "requirements.txt": "pip",
    "poetry.lock": "pip",
    "go.mod": "gomod",
    "Cargo.toml": "cargo",
}

#: ecosystems that monitor something other than a directory manifest
ECOSYSTEMS_WITHOUT_MANIFEST = {"github-actions", "docker"}


def _tracked_files() -> list[str]:
    """Tracked paths only, so an untracked scratch manifest cannot widen the requirement."""
    import subprocess

    out = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True)
    assert out.returncode == 0, "git ls-files failed -- guard cannot know the tree"
    assert out.stdout.strip(), "git ls-files returned nothing -- refusing to pass vacuously"
    return out.stdout.splitlines()


def _entries() -> list[dict]:
    doc = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert doc["version"] == 2, "dependabot config must be version 2"
    updates = doc["updates"]
    assert isinstance(updates, list) and updates, "no dependabot updates parsed"
    return updates


def _required() -> set[tuple[str, str]]:
    req = set()
    for path in _tracked_files():
        name = path.rsplit("/", 1)[-1]
        eco = MANIFESTS.get(name)
        if eco:
            directory = "/" + (path.rsplit("/", 1)[0] + "/" if "/" in path else "")
            req.add((eco, directory.replace("//", "/") or "/"))
    return req


def _declared() -> set[tuple[str, str]]:
    return {(e["package-ecosystem"], e["directory"]) for e in _entries()}


def test_every_dependency_manifest_is_monitored():
    missing = sorted(_required() - _declared())
    assert not missing, (
        f"dependency manifests with no dependabot ecosystem: {missing}. Pinning a dependency is not "
        "the same as monitoring it."
    )


def test_no_ecosystem_monitors_a_directory_with_no_manifest():
    stale = []
    for eco, directory in sorted(_declared()):
        if eco in ECOSYSTEMS_WITHOUT_MANIFEST:
            continue
        base = (ROOT / directory.strip("/")).resolve()
        if not any((base / m).exists() for m in MANIFESTS if MANIFESTS[m] == eco):
            stale.append((eco, directory))
    assert not stale, f"dependabot entries pointing at directories with no such manifest: {stale}"


def test_every_entry_is_actually_schedulable():
    """Dependabot silently ignores an entry with no schedule."""
    offenders = [e["package-ecosystem"] for e in _entries() if not (e.get("schedule") or {}).get("interval")]
    assert not offenders, f"entries with no schedule.interval (dependabot will not run them): {offenders}"


def test_workflow_ecosystem_is_present_and_root_scoped():
    """The fleet's dominant supply-chain surface is action refs, not language packages."""
    assert ("github-actions", "/") in _declared(), "github-actions ecosystem missing at root"
    workflows = [p for p in _tracked_files() if re.match(r"^\.github/workflows/.+\.ya?ml$", p)]
    assert workflows, "no workflows found -- the assertion above would be meaningless"


def test_guard_is_not_vacuous():
    required = _required()
    assert required, "no manifests detected -- coverage check cannot be proving anything"
    assert len(required) >= 2, f"expected at least pip and npm manifests in this tree, got {required}"
    declared = _declared()
    assert len(declared) >= 2, f"dependabot config parsed to too few entries: {declared}"
