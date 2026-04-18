from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient

from app.main import app


def test_full_analysis_flow():
    client = TestClient(app)
    today = date.today().isoformat()

    create_res = client.post('/api/health-records', json={
        'record_date': today,
        'weight': 75.0,
        'sleep_hours': 7.0,
        'calories': 2200,
        'protein': 90,
        'exercise_minutes': 20,
    })
    assert create_res.status_code in (201, 409)

    summary_res = client.get('/api/analytics/summary')
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert 'plateau' in summary
    assert 'recommendations' in summary

    weekly_res = client.get('/api/report/weekly')
    assert weekly_res.status_code == 200
    weekly = weekly_res.json()
    assert 'recommendations' in weekly
