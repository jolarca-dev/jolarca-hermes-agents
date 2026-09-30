# ──────────────────────────────────────────────────────────────────────────────
# jolarca-hermes-agents — Makefile
# ──────────────────────────────────────────────────────────────────────────────
# Targets: lint / typecheck / test / validate / check
# CI job `lint` runs `make check`.
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: lint typecheck test validate check agents schemas deny-patterns evals help

VENV := .venv/bin
PYTHON := $(VENV)/python
PYTEST := $(VENV)/pytest
RUFF := $(VENV)/ruff

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

lint:  ## Run ruff linter
	$(RUFF) check .

typecheck:  ## Run mypy (stub — no typed code yet)
	@echo "typecheck: no typed modules yet"

test:  ## Run pytest
	$(PYTEST) tests/ agents/ -v

validate: agents schemas  ## Run all validation targets

agents:  ## Validate agent.yaml + policy.yaml against schemas
	$(PYTHON) scripts/validate_agents.py

schemas:  ## Validate JSON Schemas are well-formed
	$(PYTHON) -c "import json, pathlib; \
		[schema and json.loads(schema) for schema in \
		[p.read_text() for p in pathlib.Path('schemas').glob('*.schema.json')]]"
	@echo "schemas: OK"

deny-patterns:  ## Scan for forbidden mission-platform references
	$(PYTHON) scripts/check_deny_patterns.py

evals:  ## Validate evaluation suite grounding + coverage (C11/C12)
	$(PYTHON) scripts/check_eval_coverage.py

check: lint validate deny-patterns  ## Full pre-merge check (CI runs this)
