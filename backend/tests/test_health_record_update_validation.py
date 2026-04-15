from __future__ import annotations

from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.health_records import router as health_records_router
from app.database import get_session
from app.models.health_record import (
    HealthRecord,  # noqa: F401  (ensure SQLModel metadata is populated)
)
from app.time import get_today


def make_client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    app.include_router(health_records_router)
    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


def create_record(client: TestClient, d: date, *, weight: float = 75.0) -> int:
    res = client.post(
        "/api/health-records",
        json={
            "record_date": d.isoformat(),
            "weight": weight,
            "sleep_hours": 7.0,
            "calories": 2000,
            "protein": 120,
            "exercise_minutes": 30,
            "exercise_type": "Walking",
            "steps": 8000,
            "note": None,
        },
    )
    assert res.status_code == 201
    payload = res.json()
    assert payload["created_at"].endswith("Z")
    assert payload["updated_at"].endswith("Z")
    return payload["id"]


def test_update_rejects_explicit_null_weight():
    client = make_client()
    rid = create_record(client, get_today())

    res = client.put(f"/api/health-records/{rid}", json={"weight": None})
    assert res.status_code == 422


def test_update_rejects_explicit_null_record_date():
    client = make_client()
    rid = create_record(client, get_today())

    res = client.put(f"/api/health-records/{rid}", json={"record_date": None})
    assert res.status_code == 422


def test_update_rejects_illegal_values():
    client = make_client()
    rid = create_record(client, get_today())

    res = client.put(f"/api/health-records/{rid}", json={"weight": -1})
    assert res.status_code == 422

    res = client.put(f"/api/health-records/{rid}", json={"sleep_hours": 25})
    assert res.status_code == 422

    res = client.put(f"/api/health-records/{rid}", json={"calories": -10})
    assert res.status_code == 422


def test_update_rejects_duplicate_record_date():
    client = make_client()
    anchor = get_today()
    other_day = anchor - timedelta(days=1)

    rid_a = create_record(client, anchor, weight=75.0)
    _rid_b = create_record(client, other_day, weight=76.0)

    res = client.put(f"/api/health-records/{rid_a}", json={"record_date": other_day.isoformat()})
    assert res.status_code == 409


def test_create_rejects_future_record_date():
    client = make_client()
    future_day = get_today() + timedelta(days=1)

    res = client.post(
        "/api/health-records",
        json={
            "record_date": future_day.isoformat(),
            "weight": 75.0,
            "sleep_hours": 7.0,
            "calories": 2000,
            "protein": 120,
            "exercise_minutes": 30,
            "exercise_type": "Walking",
            "steps": 8000,
            "note": None,
        },
    )
    assert res.status_code == 422
    assert "record_date cannot be in the future" in res.text


def test_update_rejects_future_record_date():
    client = make_client()
    rid = create_record(client, get_today())
    future_day = get_today() + timedelta(days=1)

    res = client.put(f"/api/health-records/{rid}", json={"record_date": future_day.isoformat()})
    assert res.status_code == 422
    assert "record_date cannot be in the future" in res.text
