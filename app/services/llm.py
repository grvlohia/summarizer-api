import json
import time

import structlog
from anthropic import AsyncAnthropic
from anthropic.types import TextBlock
from pydantic import ValidationError

from app.schemas import Summary

log = structlog.get_logger()


SYSTEM_PROMPT = """You are a precise editorial assistant. You receive a single article and you produce a structured summary.

You will return a JSON object with EXACTLY these fields and no others:
- "tldr": a string containing exactly two sentences summarizing the article. No more, no fewer.
- "takeaways": an array of exactly 5 strings, each a single key takeaway. Each takeaway is a complete sentence. Order from most to least important.
- "social_post": a single string, 280 characters or fewer, suitable for posting on X/Twitter. Punchy, no hashtags unless the article warrants one, no emojis.

Rules:
- Be faithful. If the article does not say something, do not say it. No outside knowledge.
- Be concise. Tighter is better, as long as nothing important is lost.
- Use plain English. No jargon unless the article uses it.
- Do not include preambles like "Here is the summary." Output only the JSON object."""

USER_PROMPT = """Here is the article:
<article>
{article}
</article>

Return only the JSON object, with no other text before or after."""


class SummarizerError(Exception):
    """Base exception for summarizer errors."""


class Summarizer:
    def __init__(self, client: AsyncAnthropic, model: str, max_tokens: int) -> None:
        self._client = client
        self._model = model
        self._max_tokens = max_tokens

    async def summarize(self, article: str) -> tuple[Summary, int, int]:
        """Returns a tuple of (summary, input_tokens, output_tokens)"""
        start = time.perf_counter()
        response = await self._client.messages.create(
            max_tokens=self._max_tokens,
            model=self._model,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": USER_PROMPT.format(article=article)}],
        )
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        block = response.content[0]
        if not isinstance(block, TextBlock):
            raise SummarizerError(f"LLM returned invalid output: {block}")

        raw = block.text
        try:
            stripped = raw.replace("```json\n", "").replace("```", "").replace("\n", "")
            parsed = json.loads(stripped)
            summary = Summary.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as e:
            log.error(
                "llm_invalid_output",
                model=self._model,
                latency_ms=latency_ms,
                raw_preview=raw[:300],
                error=str(e),
            )
            # The line below raises a custom exception and attaches the original exception (`e`) as the cause.
            # Using `from e` preserves the traceback of the original error for easier debugging,
            # making it clear that the custom exception was raised as a direct result of `e`.
            raise SummarizerError(f"LLM returned invalid output: {e}") from e

        log.info(
            "llm_call_succeeded",
            model=self._model,
            latency_ms=latency_ms,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
        return summary, response.usage.input_tokens, response.usage.output_tokens
