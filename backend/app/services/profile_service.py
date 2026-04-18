from __future__ import annotations

from sqlmodel import Session, select

from app.models.profile import Profile
from app.schemas.profile import ProfileUpdate
from app.time import utcnow


def get_or_create_profile(session: Session) -> Profile:
    profile = session.exec(select(Profile).limit(1)).first()
    if profile is None:
        profile = Profile()
        session.add(profile)
        session.commit()
        session.refresh(profile)
    return profile


def update_profile(session: Session, data: ProfileUpdate) -> Profile:
    profile = get_or_create_profile(session)
    payload = data.model_dump()
    for key, value in payload.items():
        setattr(profile, key, value)
    profile.updated_at = utcnow()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile
