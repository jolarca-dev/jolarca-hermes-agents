"""Structural guard for the revision-history tables, which no gate used to shape-check.

Motivation is a defect I made myself while preparing the markdownlint 0.41 upgrade: a revision row whose
text contained a literal pipe-dash sequence. Inside a table cell those pipes are delimiters, so a 3-cell
row became a 7-cell row -- `MD056/table-column-count` plus seven `MD060/table-column-style` findings -- and
it also broke the *currently pinned* linter. Nothing in the required `lint`/`test`/`security` contexts would
have caught it: `tests/test_ci_control_wiring.py` parses control-matrix rows, but no test looked at these
two tables. Markdownlint's supplementary job would have flagged it, which is weaker than a named assertion
that says which table is broken and why.
"""

from __future__ import annotations

import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent

REVISION_TABLES = {
    "QODER.md": "| Date | Change | Authority |",
    "docs/target-tree.md": "| Date | Change | Authority |",
}


def _revision_rows(rel: str) -> list[tuple[int, list[str]]]:
    """Rows of the revision-history table, as (line number, cells) pairs."""
    header = REVISION_TABLES[rel]
    lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(header)
    except ValueError:
        raise AssertionError(f"{rel}: revision table header {header!r} not found") from None
    rows = []
    for offset, line in enumerate(lines[start + 2 :], start + 3):
        if not line.strip():
            break
        rows.append((offset, [c.strip() for c in line.strip().strip("|").split("|")]))
    assert rows, f"{rel}: revision table has no rows"
    return rows


@pytest.mark.parametrize("rel", sorted(REVISION_TABLES))
def test_revision_tables_have_the_declared_column_count(rel: str):
    """Every row must be exactly as wide as its header, with no pipe characters in the cells."""
    width = len([c for c in REVISION_TABLES[rel].strip().strip("|").split("|")])
    bad = [(n, len(cells)) for n, cells in _revision_rows(rel) if len(cells) != width]
    assert not bad, (
        f"{rel}: revision rows must have {width} cells; found {bad}. A literal pipe inside a cell splits "
        f"it -- reword the entry (or use a fence outside the table) rather than escaping into the prose"
    )


@pytest.mark.parametrize("rel", sorted(REVISION_TABLES))
def test_revision_rows_are_newest_last_and_dated(rel: str):
    rows = _revision_rows(rel)
    dates = [cells[0] for _, cells in rows]
    assert all(d.startswith("2026-") for d in dates), f"{rel}: undated revision rows: {dates}"
    assert dates == sorted(dates), f"{rel}: revision rows are not in chronological order"
    assert all(cells[1] and cells[2] for _, cells in rows), f"{rel}: revision row with an empty cell"
