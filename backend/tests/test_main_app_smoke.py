from __future__ import annotations

from fastapi.testclient import TestClient


def test_main_app_meta_and_health():
    # Import lazily so the module-level app wiring is included in coverage.
    from app.main import app

    client = TestClient(app)

    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

    res = client.get("/api/meta")
    assert res.status_code == 200
    payload = res.json()
    assert payload["name"] == "PlateauBreaker API"
    assert "version" in payload

