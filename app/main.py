import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from anthropic import AsyncAnthropic
from fastapi import FastAPI, HTTPException, Request, Response
from starlette.middleware.base import RequestResponseEndpoint
from structlog.contextvars import bind_contextvars, clear_contextvars

from app.config import settings
from app.logging import configure_logging
from app.schemas import SummarizeRequest, SummarizeResponse
from app.services.llm import Summarizer, SummarizerError

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    client = AsyncAnthropic(
        api_key=settings.anthropic_api_key, timeout=settings.anthropic_timeout_s
    )
    app.state.summarizer = Summarizer(
        client=client,
        model=settings.anthropic_model,
        max_tokens=settings.anthropic_max_tokens,
    )
    log.info("startup", env=settings.env, model=settings.anthropic_model)
    # Initialize the Anthropic client here in Day 3.
    yield
    await client.close()
    log.info("shutdown")


app = FastAPI(title="Summarizer API", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next: RequestResponseEndpoint) -> Response:
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    clear_contextvars()
    bind_contextvars(request_id=request_id, route=request.url.path, method=request.method)
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        log.exception("unhandled_exception")
        raise
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    log.info("request_completed", status=response.status_code, latency_ms=latency_ms)
    response.headers["x-request-id"] = request_id
    return response


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    """Liveness — process is up."""
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict[str, str]:
    """Readiness — dependencies (Anthropic, in Week 2: Postgres/Redis) are reachable."""
    # In Week 1 we don't ping Anthropic on every readiness check (rate limits, cost).
    # For now, readyz == healthz. Revisit Week 2.
    return {"status": "ready"}


@app.post("/v1/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest, request: Request) -> SummarizeResponse:
    summarizer: Summarizer = request.app.state.summarizer
    try:
        summary, input_tokens, output_tokens = await summarizer.summarize(req.text)
    except SummarizerError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    return SummarizeResponse(
        summary=summary,
        model=settings.anthropic_model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
