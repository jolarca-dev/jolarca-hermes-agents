"""Guard that an installed pre-commit hook cannot silently restyle governance document headers.

The latent defect: `.pre-commit-config.yaml` declared `trailing-whitespace` with no arguments while
three `Status: Accepted` governance docs open with markdown **hard line breaks** -- lines ending in two
spaces -- in their metadata headers. Installing the hook and committing any edit to those files strips
the spaces, and in two of the three files the following metadata line has *no* hard break, so
`**Status:** Accepted **Date:** 2026-09-30 **ADR prefix:** HERMES-` collapses into one rendered
paragraph. The damage is a change to how compliance metadata displays, produced by an unrelated commit.

markdownlint is NOT the problem here: under this repo's `.markdownlint.json`, `MD009` runs with
`strict: false`, so two-space hard breaks are permitted and reported zero findings. The conflict belongs
to the hook alone. See `QODER.md` §7.10.
"""

from __future__ import annotations

import pathlib
import re
import subprocess

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".pre-commit-config.yaml"


def _hook(hook_id: str) -> dict:
    doc = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    for repo in doc["repos"]:
        for hook in repo["hooks"]:
            if hook["id"] == hook_id:
                return hook
    raise AssertionError(f"hook {hook_id!r} is no longer declared in .pre-commit-config.yaml")


def test_trailing_whitespace_hook_preserves_markdown_line_breaks():
    """Mitigation must be `--markdown-linebreak-ext=md`, not a docs-wide exclusion.

    An `exclude:` for `docs/` would also stop the hook catching real trailing whitespace anywhere in
    the governance corpus -- weakening the very control it is meant to protect.
    """
    args = [str(a) for a in (_hook("trailing-whitespace").get("args") or [])]
    joined = " ".join(args)
    assert "--markdown-linebreak-ext" in joined, (
        f"`trailing-whitespace` has no markdown linebreak mitigation; installing the hook strips "
        f"the hard breaks in docs/capability-map.md, docs/control-matrix.md and docs/target-tree.md: {args}"
    )
    assert re.search(r"--markdown-linebreak-ext=?\S*md", joined), (
        f"mitigation present but does not cover markdown: {args}"
    )


def test_mitigation_is_not_replaced_by_an_exclusion():
    hook = _hook("trailing-whitespace")
    assert not hook.get("exclude"), (
        "`trailing-whitespace` was softened with an exclude; that removes coverage instead of protecting the construct"
    )


def test_hard_break_construct_still_exists_so_the_mitigation_is_load_bearing():
    """If these lines vanish someday, the arg becomes harmless -- but say so loudly, not silently."""
    files = subprocess.run(["git", "ls-files", "*.md"], capture_output=True, text=True, cwd=ROOT).stdout.split()
    hits = [
        (f, i)
        for f in files
        for i, line in enumerate((ROOT / f).read_text(encoding="utf-8").splitlines(), 1)
        if line.endswith("  ") and line.strip()
    ]
    assert hits, (
        "no two-space hard breaks remain in tracked markdown; the mitigation is now decorative and "
        "this guard should be retired deliberately, not left asserting nothing"
    )
    print(f"hard-break lines protected: {len(hits)} -> {hits}")


def test_every_hook_revision_is_a_pinned_version_not_a_branch():
    """pre-commit fetches these at commit time; a branch ref would float under our feet."""
    doc = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    floats = [
        f"{r['repo']}@{r.get('rev')}"
        for r in doc["repos"]
        if not re.match(r"^v?\d+\.\d+(\.\d+)?$", str(r.get("rev") or ""))
    ]
    assert not floats, f"hook repos not pinned to an exact version tag: {floats}"
