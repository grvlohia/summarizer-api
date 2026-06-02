import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from anthropic import AsyncAnthropic
from anthropic.types import TextBlock

from app.services.llm import Summarizer, SummarizerError


@pytest.fixture
def fake_client() -> MagicMock:
    client = MagicMock(spec=AsyncAnthropic)
    client.messages = MagicMock()
    client.messages.create = AsyncMock()
    return client


def _fake_response(
    payload: dict[str, object] | str, input_tokens: int = 100, output_tokens: int = 80
) -> MagicMock:
    body = json.dumps(payload) if isinstance(payload, dict) else payload
    return MagicMock(
        content=[MagicMock(spec=TextBlock, text=body)],
        usage=MagicMock(input_tokens=input_tokens, output_tokens=output_tokens),
    )


async def test_summarize_happy_path(fake_client: MagicMock) -> None:
    fake_client.messages.create.return_value = _fake_response(
        {
            "tldr": "First sentence. Second sentence.",
            "takeaways": [f"Takeaway {i}." for i in range(1, 6)],
            "social_post": "A punchy line under 280 chars.",
        }
    )

    s = Summarizer(client=fake_client, model="claude-haiku-4-5", max_tokens=1024)
    summary, in_tok, out_tok = await s.summarize("x" * 400)
    assert len(summary.takeaways) == 5
    assert in_tok == 100
    assert out_tok == 80


async def test_summarize_rejects_non_json(fake_client: MagicMock) -> None:
    fake_client.messages.create.return_value = _fake_response("Not a JSON object")
    s = Summarizer(client=fake_client, model="claude-haiku-4-5", max_tokens=1024)
    with pytest.raises(SummarizerError):
        await s.summarize("x" * 400)


async def test_summarize_rejects_wrong_takeaway_count(fake_client: MagicMock) -> None:
    fake_client.messages.create.return_value = _fake_response(
        {
            "tldr": "One. Two.",
            "takeaways": ["only one"],  # violates min_length=5
            "social_post": "ok",
        }
    )
    s = Summarizer(client=fake_client, model="claude-haiku-4-5", max_tokens=1024)
    with pytest.raises(SummarizerError):
        await s.summarize("x" * 400)
