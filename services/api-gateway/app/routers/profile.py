from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Profile, User
from ..schemas import ProfileCreate, ProfileResponse

router = APIRouter(prefix="/v1/profile", tags=["profile"])


@router.post("", response_model=ProfileResponse, status_code=201)
def create_profile(
    req: ProfileCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProfileResponse:
    profile = Profile(user_id=user.id, **req.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProfileResponse:
    profile = db.query(Profile).filter(
        Profile.id == profile_id,
        Profile.user_id == user.id,
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
