import pytest
from fastapi.testclient import TestClient

from app.main import app

SAMPLE_ARTICLE = """
The James Webb Space Telescope, launched in December 2021, has revolutionized our view of the
early universe. Its infrared instruments can peer through cosmic dust to see star formation
in real time. Within its first year of science operations, it identified galaxies that appear
to have formed within a few hundred million years of the Big Bang — far earlier than current
cosmological models comfortably predict. Astronomers are now debating whether these findings
require revisions to the standard model of structure formation, or whether the apparent ages
of these galaxies are being overestimated due to dust effects in their light. Either way, the
telescope is performing well beyond its design specifications, and is expected to operate for
at least 20 years thanks to fuel-efficient orbit corrections during launch.
""".strip()


@pytest.mark.integration
def test_summarize_real_anthropic_call() -> None:
    with TestClient(app) as client:
        r = client.post("/v1/summarize", json={"text": SAMPLE_ARTICLE})
        assert r.status_code == 200, r.text
        body = r.json()
        assert "summary" in body
        assert len(body["summary"]["takeaways"]) == 5
        assert len(body["summary"]["social_post"]) <= 280
        assert body["input_tokens"] > 0
        assert body["output_tokens"] > 0
