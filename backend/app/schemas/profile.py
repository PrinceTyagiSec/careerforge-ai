from pydantic import BaseModel
from typing import Optional, List, Any
import datetime

class CandidateProfileUpdate(BaseModel):
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    remote_preference: Optional[str] = None
    target_role: Optional[str] = None
    years_of_experience: Optional[float] = None
    expected_salary_min: Optional[float] = None
    expected_salary_max: Optional[float] = None
    currency: Optional[str] = "INR"
    availability: Optional[str] = None
    work_authorization: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    phone: Optional[str] = None

class CandidateProfileResponse(BaseModel):
    id: int
    user_id: int
    headline: Optional[str]
    summary: Optional[str]
    location: str
    remote_preference: str
    target_role: Optional[str]
    years_of_experience: float
    expected_salary_min: Optional[float]
    expected_salary_max: Optional[float]
    currency: str
    availability: Optional[str]
    work_authorization: Optional[str]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    phone: Optional[str]
    updated_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True

class JobPreferenceUpdate(BaseModel):
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    min_salary: Optional[float] = None
    currency: Optional[str] = "INR"
    remote_only: Optional[bool] = False
