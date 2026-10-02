from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

class JobSourceResponse(BaseModel):
    id: int
    provider_name: str
    external_id: Optional[str]
    source_url: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class JobRequirementResponse(BaseModel):
    id: int
    category: str
    requirement_text: str
    canonical_term: str
    is_mandatory: bool

    class Config:
        from_attributes = True

class JobItemResponse(BaseModel):
    id: int
    title: str
    company_name: str
    location: str
    city: Optional[str]
    remote_status: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_currency: str
    employment_type: str
    experience_min_years: Optional[float]
    description: str
    canonical_url: str
    freshness_status: str
    is_url_valid: bool
    published_at: Optional[datetime.datetime]
    discovered_at: Optional[datetime.datetime]
    sources: List[JobSourceResponse] = []
    requirements: List[JobRequirementResponse] = []
    
    # Match data if matched for current user
    match_score: Optional[float] = None
    matching_skills: List[str] = []
    missing_skills: List[str] = []
    is_saved: bool = False
    application_status: Optional[str] = None

    class Config:
        from_attributes = True

class JobImportRequest(BaseModel):
    import_type: str # "url" | "text"
    url: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = "India"
    description: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None

class JobSearchFilter(BaseModel):
    keywords: Optional[str] = None
    location: Optional[str] = None
    remote_status: Optional[str] = None # "All", "Remote", "Hybrid", "On-site"
    min_salary: Optional[float] = None
    experience_level: Optional[str] = None
    source: Optional[str] = None
    freshness: Optional[str] = None # "Fresh", "Recently Updated"
    min_match_score: Optional[float] = None
    saved_only: bool = False
    page: int = 1
    page_size: int = 20
