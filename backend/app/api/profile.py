from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services import profile_service

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(session: Session = Depends(get_session)) -> ProfileResponse:
    profile = profile_service.get_or_create_profile(session)
    return ProfileResponse.model_validate(profile)


@router.put("", response_model=ProfileResponse)
def put_profile(data: ProfileUpdate, session: Session = Depends(get_session)) -> ProfileResponse:
    profile = profile_service.update_profile(session, data)
    return ProfileResponse.model_validate(profile)
