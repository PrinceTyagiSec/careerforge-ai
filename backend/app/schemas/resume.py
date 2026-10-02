from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

class SkillSchema(BaseModel):
    id: Optional[int] = None
    name: str
    canonical_name: str
    category: str
    proficiency: str = "Intermediate"
    verification_status: str = "Verified"

class ExperienceSchema(BaseModel):
    id: Optional[int] = None
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    bullets: List[str] = []

class EducationSchema(BaseModel):
    id: Optional[int] = None
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ProjectSchema(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    technologies: List[str] = []
    bullets: List[str] = []
    url: Optional[str] = None

class SectionUpdate(BaseModel):
    heading: Optional[str] = None
    content: Optional[str] = None
    order_index: Optional[int] = None
    is_enabled: Optional[bool] = None

class ClaimResponse(BaseModel):
    id: int
    category: str
    statement: str
    source_section: Optional[str]
    source_snippet: Optional[str]
    verification_status: str
    confidence: float

    class Config:
        from_attributes = True

class ResumeDetailResponse(BaseModel):
    id: int
    original_filename: str
    file_type: str
    raw_text: Optional[str]
    ocr_applied: bool
    ocr_confidence: Optional[float]
    parsing_status: str
    skills: List[SkillSchema]
    experiences: List[ExperienceSchema]
    educations: List[EducationSchema]
    projects: List[ProjectSchema]
    claims: List[ClaimResponse]
    created_at: datetime.datetime

    class Config:
        from_attributes = True
