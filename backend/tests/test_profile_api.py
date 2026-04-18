from __future__ import annotations

from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.profile import router as profile_router
from app.database import get_session
from app.models import Profile


def make_client() -> TestClient:
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    app.include_router(profile_router)
    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


def test_profile_get_and_put():
    client = make_client()

    get_res = client.get('/api/profile')
    assert get_res.status_code == 200
    assert get_res.json()['daily_calorie_target'] == 2000

    put_res = client.put('/api/profile', json={
        'target_weight': 70.5,
        'daily_calorie_target': 2100,
        'protein_target': 130,
        'weekly_workout_target': 5,
    })
    assert put_res.status_code == 200
    body = put_res.json()
    assert body['target_weight'] == 70.5
    assert body['daily_calorie_target'] == 2100
