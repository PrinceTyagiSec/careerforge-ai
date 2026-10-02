from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

class SavedSearchCreate(BaseModel):
    name: str
    keywords: Optional[str] = None
    location: Optional[str] = "Remote India"
    remote_preference: Optional[str] = "Flexible"
    min_salary: Optional[float] = None
    experience_level: Optional[str] = None
    frequency_minutes: int = 360
    notify_telegram: bool = True
    min_match_threshold: float = 75.0

class SavedSearchResponse(BaseModel):
    id: int
    name: str
    keywords: Optional[str]
    location: str
    remote_preference: str
    min_salary: Optional[float]
    experience_level: Optional[str]
    is_enabled: bool
    frequency_minutes: int
    last_run_at: Optional[datetime.datetime]
    next_run_at: Optional[datetime.datetime]
    total_found_count: int
    new_jobs_count: int
    high_match_count: int
    notify_telegram: bool
    min_match_threshold: float
    created_at: datetime.datetime

    class Config:
        from_attributes = True
