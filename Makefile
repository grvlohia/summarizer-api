.DEFAULT_GOAL := help
APP := app.main:app

.PHONY: help install dev prod lint format typecheck test test-integration check clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ─────────────────────────────────────────────────────────────────────

install: ## Install all dependencies (including dev)
	uv sync --all-groups
	uv run pre-commit install

# ── Development ───────────────────────────────────────────────────────────────

dev: ## Start dev server with auto-reload
	uv run fastapi dev app/main.py

# ── Production ────────────────────────────────────────────────────────────────

prod: ## Start production server (4 workers)
	uv run uvicorn $(APP) --host 0.0.0.0 --port 8000 --workers 4

# ── Code Quality ──────────────────────────────────────────────────────────────

lint: ## Run ruff linter (auto-fix)
	uv run ruff check --fix .

format: ## Run ruff formatter
	uv run ruff format .

typecheck: ## Run mypy type checker
	uv run mypy .

check: lint format typecheck ## Run all checks (lint + format + typecheck)

# ── Tests ─────────────────────────────────────────────────────────────────────

test: ## Run unit tests (excludes integration tests)
	uv run pytest

test-integration: ## Run integration tests (hits real external services)
	uv run pytest -m integration

# ── Misc ──────────────────────────────────────────────────────────────────────

clean: ## Remove cache and build artifacts
	rm -rf .venv .mypy_cache .ruff_cache .pytest_cache __pycache__
