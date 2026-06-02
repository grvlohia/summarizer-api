from fastapi.testclient import TestClient

from app.main import app


def test_healthz() -> None:
    with TestClient(app) as client:
        r = client.get("/healthz")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


def test_request_id_round_trip() -> None:
    with TestClient(app) as client:
        r = client.get("/healthz", headers={"x-request-id": "deadbeef"})
        assert r.headers["x-request-id"] == "deadbeef"
