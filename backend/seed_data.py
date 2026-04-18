from __future__ import annotations

import argparse
import os
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, delete

from app.database import DATABASE_URL, create_db_and_tables, engine
from app.models.health_record import HealthRecord

random.seed(42)


def _base_record(d: date) -> dict:
    return {
        'record_date': d,
        'weight': 75.0,
        'sleep_hours': 7.0,
        'calories': 2000,
        'protein': 120,
        'exercise_minutes': 30,
        'exercise_type': 'Walking',
        'steps': 8000,
        'note': None,
    }


def scenario_healthy_progress(days: int = 30) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows: list[dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        r = _base_record(d)
        r['weight'] = round(78.0 - i * 0.12, 1)
        r['calories'] = 1800
        r['protein'] = 140
        rows.append(r)
    return rows


def scenario_plateau_case(days: int = 30) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows: list[dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        r = _base_record(d)
        r['weight'] = round(75.0 + random.uniform(-0.2, 0.2), 1)
        r['calories'] = 2250
        r['sleep_hours'] = 5.8
        rows.append(r)
    return rows


def scenario_missing_data_case(days: int = 30) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows: list[dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        if i % 5 == 0:
            continue
        rows.append(_base_record(d))
    return rows


def scenario_high_calorie_case(days: int = 30) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows: list[dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        r = _base_record(d)
        r['calories'] = 2800 if d.weekday() >= 5 else 2400
        r['weight'] = round(74.0 + i * 0.08, 1)
        rows.append(r)
    return rows


SCENARIOS = {
    'healthy_progress': scenario_healthy_progress,
    'plateau_case': scenario_plateau_case,
    'missing_data_case': scenario_missing_data_case,
    'high_calorie_case': scenario_high_calorie_case,
}


def seed(scenario: str) -> None:
    create_db_and_tables()
    print(f'Database: {DATABASE_URL}')

    rows = SCENARIOS[scenario]()
    with Session(engine) as session:
        session.exec(delete(HealthRecord))
        for r in rows:
            session.add(HealthRecord(**r))
        session.commit()

    print(f'Seeded scenario={scenario} with {len(rows)} records.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', choices=sorted(SCENARIOS.keys()), default='plateau_case')
    args = parser.parse_args()
    seed(args.scenario)
