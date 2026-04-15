from datetime import date, datetime
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

from app.time import utcnow


class HealthRecord(SQLModel, table=True):
    __tablename__ = "health_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    record_date: date = Field(index=True, unique=True)
    weight: float
    sleep_hours: float
    calories: int
    protein: Optional[int] = Field(default=None)
    exercise_minutes: int = Field(default=0)
    exercise_type: Optional[str] = Field(default=None, max_length=50)
    steps: Optional[int] = Field(default=None)
    note: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
