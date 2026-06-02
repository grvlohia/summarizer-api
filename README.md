# Summarizer API

A REST service that turns article text into a 2-sentence TL;DR, 5 key takeaways,
and a Twitter-length variant. Backed by Claude Haiku 4.5.

## Quick start
1. `cp .env.example .env` and fill in `ANTHROPIC_API_KEY`.
2. `uv sync`
3. `uv run uvicorn app.main:app --reload`
4. Open http://localhost:8000/docs

## API
- `GET /healthz` — liveness
- `GET /readyz` — readiness
- `POST /v1/summarize` — body: `{"text": "..."}`. See `/docs` for the response schema.

## Dev
- `uv run pytest` — unit tests
- `uv run pytest -m integration` — hits real Anthropic API; needs ANTHROPIC_API_KEY
- `uv run ruff check . && uv run mypy app`

## Architecture
(insert Excalidraw diagram in Week 4)

## Design decisions
See `docs/design/01-summarizer-api.md`.