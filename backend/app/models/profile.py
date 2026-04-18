from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

from app.time import utcnow


class Profile(SQLModel, table=True):
    __tablename__ = "profile"

    id: Optional[int] = Field(default=1, primary_key=True)
    target_weight: Optional[float] = Field(default=None, ge=20, le=500)
    daily_calorie_target: int = Field(default=2000, ge=1000, le=5000)
    protein_target: Optional[int] = Field(default=None, ge=0, le=500)
    weekly_workout_target: Optional[int] = Field(default=None, ge=0, le=50)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
