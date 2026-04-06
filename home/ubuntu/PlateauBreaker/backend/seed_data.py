"""
Seed script — generates 30 days of realistic health records for testing.
Run: python3.11 seed_data.py

Simulates a realistic plateau scenario:
  - Days 1–10: Gradual weight loss (75 → 73 kg)
  - Days 11–20: Plateau (weight stagnates around 73 kg)
  - Days 21–30: Slight recovery attempt
"""
import random
import sys
import os
from datetime import date, timedelta

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import create_db_and_tables, engine
from app.models.health_record import HealthRecord
from sqlmodel import Session, select

random.seed(42)

EXERCISE_TYPES = ["Running", "Cycling", "Walking", "Gym", "Swimming", "Yoga", "HIIT", "Rest"]


def generate_records(days: int = 30) -> list[dict]:
    records = []
    today = date.today()
    start_date = today - timedelta(days=days - 1)

    base_weight = 75.0

    for i in range(days):
        d = start_date + timedelta(days=i)
        weekday = d.weekday()  # 0=Mon, 6=Sun
        is_weekend = weekday >= 5

        # Weight trajectory
        if i < 10:
            # Losing phase
            weight = base_weight - (i * 0.2) + random.uniform(-0.15, 0.15)
        elif i < 20:
            # Plateau phase — minimal change
            weight = 73.0 + random.uniform(-0.25, 0.25)
        else:
            # Slight rebound
            weight = 73.0 + (i - 20) * 0.05 + random.uniform(-0.2, 0.2)

        weight = round(weight, 1)

        # Sleep — some bad nights
        if i in [5, 12, 18, 24]:
            sleep = round(random.uniform(4.5, 5.5), 1)
        else:
            sleep = round(random.uniform(6.5, 8.5), 1)

        # Calories — weekends higher
        if is_weekend:
            calories = random.randint(2200, 2800)
        else:
            calories = random.randint(1700, 2100)

        # Protein
        protein = random.randint(80, 160)

        # Exercise — drop in plateau phase
        if i < 10:
            exercise_min = random.choice([30, 40, 45, 50, 60])
            exercise_type = random.choice(["Running", "Cycling", "HIIT", "Gym"])
        elif i < 20:
            # Exercise drop during plateau
            exercise_min = random.choice([0, 0, 15, 20, 30])
            exercise_type = random.choice(["Walking", "Rest", "Rest", "Yoga"])
        else:
            exercise_min = random.choice([20, 30, 40, 45])
            exercise_type = random.choice(["Running", "Walking", "Gym"])

        # Steps
        steps = random.randint(4000, 12000)

        # Notes
        notes_pool = [
            "Feeling good today",
            "Tired after work",
            "Had a big dinner",
            "Skipped workout",
            "Great run this morning",
            "Stress eating",
            "Slept poorly",
            None, None, None,
        ]
        note = random.choice(notes_pool)

        records.append({
            "record_date": d,
            "weight": weight,
            "sleep_hours": sleep,
            "calories": calories,
            "protein": protein,
            "exercise_minutes": exercise_min,
            "exercise_type": exercise_type,
            "steps": steps,
            "note": note,
        })

    return records


def seed():
    print("Creating database tables...")
    create_db_and_tables()

    with Session(engine) as session:
        # Check if data already exists
        existing = session.exec(select(HealthRecord)).first()
        if existing:
            print(f"Database already has records. Skipping seed.")
            print("To re-seed, delete 'plateaubreaker.db' and run again.")
            return

        records = generate_records(30)
        print(f"Inserting {len(records)} records...")

        for r in records:
            record = HealthRecord(**r)
            session.add(record)

        session.commit()
        print(f"✅ Seeded {len(records)} health records successfully!")
        print(f"   Date range: {records[0]['record_date']} → {records[-1]['record_date']}")
        print(f"   Weight range: {min(r['weight'] for r in records)} – {max(r['weight'] for r in records)} kg")


if __name__ == "__main__":
    seed()
