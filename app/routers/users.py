from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.models import Profile

router = APIRouter(prefix="/user", tags=["user"])


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    store_name: Optional[str] = None
    contact_number: Optional[str] = None


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    full_name: Optional[str] = None
    role: Optional[str] = None
    store_name: Optional[str] = None
    contact_number: Optional[str] = None


@router.get("/profile", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.id == user["sub"]).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/profile", response_model=ProfileOut)
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    profile = db.query(Profile).filter(Profile.id == user["sub"]).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


# NOTE: change-password and email/password auth itself are handled directly by
# the Supabase Auth client SDK from the Android app (supabase.auth.updateUser,
# supabase.auth.resetPasswordForEmail, etc.) rather than through this API —
# there's no password data in our own database to change. /user/notifications
# is left as a placeholder until a notifications table/feature exists.
