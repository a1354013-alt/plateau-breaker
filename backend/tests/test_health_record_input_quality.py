from __future__ import annotations

from datetime import timedelta

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


def test_note_and_exercise_type_are_trimmed_and_normalized():
    client = make_client()
    record_date = get_today() - timedelta(days=1)

    res = client.post(
        "/api/health-records",
        json={
            "record_date": record_date.isoformat(),
            "weight": 75.0,
            "sleep_hours": 7.0,
            "calories": 2000,
            "protein": 120,
            "exercise_minutes": 30,
            "exercise_type": "  Walk   ing  ",
            "steps": 8000,
            "note": "  hello  ",
        },
    )
    assert res.status_code == 201
    payload = res.json()
    assert payload["exercise_type"] == "Walk ing"
    assert payload["note"] == "hello"

    rid = payload["id"]
    res = client.put(f"/api/health-records/{rid}", json={"note": "   "})
    assert res.status_code == 200
    assert res.json()["note"] is None


def test_numeric_fields_have_upper_bounds():
    client = make_client()
    record_date = get_today() - timedelta(days=1)

    res = client.post(
        "/api/health-records",
        json={
            "record_date": record_date.isoformat(),
            "weight": 75.0,
            "sleep_hours": 7.0,
            "calories": 999999,
            "protein": 120,
            "exercise_minutes": 30,
        },
    )
    assert res.status_code == 422

    res = client.post(
        "/api/health-records",
        json={
            "record_date": record_date.isoformat(),
            "weight": 75.0,
            "sleep_hours": 7.0,
            "calories": 2000,
            "protein": 999999,
            "exercise_minutes": 30,
        },
    )
    assert res.status_code == 422

    res = client.post(
        "/api/health-records",
        json={
            "record_date": record_date.isoformat(),
            "weight": 75.0,
            "sleep_hours": 7.0,
            "calories": 2000,
            "protein": 120,
            "exercise_minutes": 30,
            "steps": 999999999,
        },
    )
    assert res.status_code == 422

