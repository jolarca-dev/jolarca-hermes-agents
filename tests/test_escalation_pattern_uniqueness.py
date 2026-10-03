"""Guard that escalation pattern tokens do not collide across the fleet.

Measured on main before this change: the twelve agents declared 28 distinct
`escalation.patterns` tokens and exactly **one** was shared — `drift_detected`, used by both
`audit` (evidence and audit-log integrity, alongside `audit_log_tampering_attempt`) and
`observability` (model/eval drift, alongside `error_rate_spike` and
`cost_ceiling_approached`). Two different incidents carrying one name means a runtime routing
alerts on pattern name alone double-fires; sibling patterns disambiguate in context, a
name-keyed router does not read context.

That collision is now **resolved by qualifying both tokens** — `audit_log_drift_detected` and
`model_eval_drift_detected` — matching the style already used beside them in the same files.
Nothing consumed the old token: `git grep drift_detected` matched only the two `policy.yaml`
files plus prose, no script, test or eval case.

`KNOWN_COLLISIONS` is therefore **locked empty**, and this suite enforces zero tolerance
instead of the ratchet it shipped as. A non-empty whitelist leaves a loophole: a new
collision could be excused by adding it to the register, and *both* the "no new collision"
and "no stale entry" tests would then pass. Pinning it empty means any future collision fails
CI and must be argued into an explicit exception rather than absorbed silently.
"""

from __future__ import annotations

import collections
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POLICIES = sorted((ROOT / "agents").glob("*/policy.yaml"))

# Debt register. Retired 2026-10-03 when `drift_detected` was qualified per emitter; kept as
# a named, empty register so an exception stays visible rather than becoming a code path.
# test_debt_register_stays_empty forbids adding to it without an explicit decision.
KNOWN_COLLISIONS: frozenset[str] = frozenset()

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
    """With an empty baseline this is zero tolerance: no two agents may share a token."""
    new = sorted(_collisions() - KNOWN_COLLISIONS)
    assert not new, f"escalation pattern token(s) newly shared across agents: {new}"


def test_debt_register_stays_empty():
    """Whitelisting a collision has to be a decision, not a default escape hatch."""
    assert not KNOWN_COLLISIONS, (
        f"KNOWN_COLLISIONS gained entries: {sorted(KNOWN_COLLISIONS)} — fix the collision by "
        "qualifying the token per emitter, as drift_detected was, rather than excusing it here"
    )


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
