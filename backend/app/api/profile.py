import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.user_helper import get_or_create_default_user
from app.models.user import User, CandidateProfile, JobPreference
from app.schemas.profile import CandidateProfileUpdate, CandidateProfileResponse, JobPreferenceUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("", response_model=CandidateProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    profile = user.profile
    if not profile:
        profile = CandidateProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("", response_model=CandidateProfileResponse)
def update_profile(data: CandidateProfileUpdate, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    profile = user.profile
    if not profile:
        profile = CandidateProfile(user_id=user.id)
        db.add(profile)

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile

@router.get("/preferences")
def get_preferences(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    pref = user.job_preferences
    if not pref:
        pref = JobPreference(user_id=user.id)
        db.add(pref)
        db.commit()
        db.refresh(pref)

    return {
        "preferred_roles": json.loads(pref.preferred_roles or "[]"),
        "preferred_locations": json.loads(pref.preferred_locations or "[]"),
        "preferred_skills": json.loads(pref.preferred_skills or "[]"),
        "min_salary": pref.min_salary,
        "currency": pref.currency,
        "remote_only": pref.remote_only
    }

@router.put("/preferences")
def update_preferences(data: JobPreferenceUpdate, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    pref = user.job_preferences
    if not pref:
        pref = JobPreference(user_id=user.id)
        db.add(pref)

    if data.preferred_roles is not None:
        pref.preferred_roles = json.dumps(data.preferred_roles)
    if data.preferred_locations is not None:
        pref.preferred_locations = json.dumps(data.preferred_locations)
    if data.preferred_skills is not None:
        pref.preferred_skills = json.dumps(data.preferred_skills)
    if data.min_salary is not None:
        pref.min_salary = data.min_salary
    if data.currency is not None:
        pref.currency = data.currency
    if data.remote_only is not None:
        pref.remote_only = data.remote_only

    db.commit()
    return {"message": "Preferences updated successfully"}
