from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

class ApplicationEventResponse(BaseModel):
    id: int
    event_type: str
    title: str
    description: Optional[str]
    occurred_at: datetime.datetime

    class Config:
        from_attributes = True

class ApplicationNoteResponse(BaseModel):
    id: int
    content: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class ApplicationCreateRequest(BaseModel):
    job_id: int
    status: str = "Applied" # Interested, Saved, Applied, Assessment, Interview, Technical Interview, HR Interview, Offer, Rejected, Withdrawn, Closed
    applied_at: Optional[datetime.datetime] = None
    follow_up_date: Optional[datetime.datetime] = None
    interview_date: Optional[datetime.datetime] = None
    deadline_date: Optional[datetime.datetime] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    salary_offered: Optional[float] = None
    notes: Optional[str] = None
    acknowledge_duplicate: bool = False

class ApplicationStatusUpdateRequest(BaseModel):
    status: str
    follow_up_date: Optional[datetime.datetime] = None
    interview_date: Optional[datetime.datetime] = None
    salary_offered: Optional[float] = None
    outcome: Optional[str] = None
    event_title: Optional[str] = None
    event_description: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    job_title: str
    company_name: str
    location: str
    status: str
    applied_at: datetime.datetime
    follow_up_date: Optional[datetime.datetime]
    interview_date: Optional[datetime.datetime]
    deadline_date: Optional[datetime.datetime]
    salary_offered: Optional[float]
    outcome: Optional[str]
    events: List[ApplicationEventResponse] = []
    notes: List[ApplicationNoteResponse] = []

    class Config:
        from_attributes = True
