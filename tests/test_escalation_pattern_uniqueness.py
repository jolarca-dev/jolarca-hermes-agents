"""Guard that escalation pattern tokens do not collide across the fleet.

Measured on main: the twelve agents declare 28 distinct `escalation.patterns` tokens and
exactly **one** is shared — `drift_detected`, declared by both `audit` (evidence and
audit-log integrity, alongside `audit_log_tampering_attempt`) and `observability`
(model/eval drift, alongside `error_rate_spike` and `cost_ceiling_approached`). Those are
different incidents that happen to share a name, so a runtime routing alerts on pattern
name alone would double-fire. Sibling patterns disambiguate in context; a name-keyed
router does not read context.

Renaming is mechanically safe — `git grep drift_detected` matches only the two
`policy.yaml` files plus prose in `CHANGELOG.md` and `docs/tool-register.md`. No script,
test or eval case consumes the token. But the replacement names are control vocabulary, so
that decision belongs to the operator, not to this guard.

This suite is therefore a **ratchet**, not a blanket rule. `KNOWN_COLLISIONS` is a
shrink-only baseline: any brand-new collision fails immediately, and retiring a listed one
also fails until the baseline entry is deleted, which forces the existing debt to be
closed explicitly instead of being absorbed as normal.
"""

from __future__ import annotations

import collections
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POLICIES = sorted((ROOT / "agents").glob("*/policy.yaml"))

# Debt register. Delete an entry when its collision is resolved; adding one requires
# justifying two agents raising the same alert name for the same incident.
KNOWN_COLLISIONS: frozenset[str] = frozenset({"drift_detected"})

VALID_ACTIONS = frozenset({"block", "escalate"})


def _escalation() -> list[tuple[str, dict]]:
    out: list[tuple[str, dict]] = []
    for path in POLICIES:
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        out.append((path.parent.name, doc.get("escalation") or {}))
    return out


def _collisions() -> set[str]:
    holders: collections.defaultdict[list[str]] = collections.defaultdict(list)
    for name, esc in _escalation():
        for token in esc.get("patterns") or []:
            holders[token].append(name)
    return {token for token, owners in holders.items() if len(owners) > 1}


def test_no_new_escalation_pattern_collisions():
    """A collision beyond the baseline is a routing ambiguity waiting to fire twice."""
    new = sorted(_collisions() - KNOWN_COLLISIONS)
    assert not new, f"escalation pattern token(s) newly shared across agents: {new}"


def test_baseline_cannot_silently_absorb_the_debt():
    """Retiring a collision must empty its baseline entry, not leave it stale."""
    stale = sorted(KNOWN_COLLISIONS - _collisions())
    assert not stale, (
        f"collision(s) listed in KNOWN_COLLISIONS no longer exist: {stale} — "
        "delete them from the baseline so the register reflects real debt"
    )


def test_every_escalation_block_declares_a_known_action():
    """A typo in `action` would make an escalation silently do nothing."""
    offenders = [
        f"{name}: action={esc.get('action')!r}" for name, esc in _escalation() if esc.get("action") not in VALID_ACTIONS
    ]
    assert not offenders, f"agent(s) with missing or unknown escalation.action: {offenders}"


def test_guard_is_not_vacuous():
    """Zero parsed patterns would make every assertion above pass trivially."""
    rows = _escalation()
    assert len(rows) == 12, f"parsed {len(rows)} policy.yaml files, expected 12"
    tokens = {t for _, esc in rows for t in (esc.get("patterns") or [])}
    assert len(tokens) >= 25, f"only {len(tokens)} escalation tokens parsed"
    assert _collisions() == set(KNOWN_COLLISIONS), "baseline has drifted from the measured fleet"
