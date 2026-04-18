from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from app.time import format_datetime_utc_z


class ProfileResponse(BaseModel):
    id: int
    target_weight: Optional[float] = None
    daily_calorie_target: int
    protein_target: Optional[int] = None
    weekly_workout_target: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", "updated_at")
    def serialize_utc_z(self, value: datetime) -> str:
        return format_datetime_utc_z(value)


class ProfileUpdate(BaseModel):
    target_weight: Optional[float] = Field(default=None, ge=20, le=500)
    daily_calorie_target: int = Field(default=2000, ge=1000, le=5000)
    protein_target: Optional[int] = Field(default=None, ge=0, le=500)
    weekly_workout_target: Optional[int] = Field(default=None, ge=0, le=50)
