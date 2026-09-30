#!/usr/bin/env python3
"""C14: Validate retention periods match the retention policy.

jolarca-hermes-agents — marketplace (jolarca-dev) agent fleet.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    errors: list[str] = []

    # Audit: 7-year retention (2555 days)
    audit_file = BASE_DIR / "agents" / "audit" / "policy.yaml"
    if audit_file.exists():
        with open(audit_file) as f:
            policy = yaml.safe_load(f)
        retention = policy.get("retention", {})
        if retention.get("max_days") != 2555:
            errors.append(f"audit retention is {retention.get('max_days')}, expected 2555 (7 years)")

    # Editorial: 7-year retention (2555 days)
    editorial_file = BASE_DIR / "agents" / "editorial" / "policy.yaml"
    if editorial_file.exists():
        with open(editorial_file) as f:
            policy = yaml.safe_load(f)
        retention = policy.get("retention", {})
        if retention.get("max_days") != 2555:
            errors.append(f"editorial retention is {retention.get('max_days')}, expected 2555 (7 years)")

    # Consent: 30-day retention (GDPR)
    consent_file = BASE_DIR / "agents" / "consent" / "policy.yaml"
    if consent_file.exists():
        with open(consent_file) as f:
            policy = yaml.safe_load(f)
        retention = policy.get("retention", {})
        if retention.get("max_days") != 30:
            errors.append(f"consent retention is {retention.get('max_days')}, expected 30 (GDPR)")

    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    print("PASSED — check_retention")
    return 0


if __name__ == "__main__":
    sys.exit(main())
