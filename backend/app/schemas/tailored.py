from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

class TailoredChangeResponse(BaseModel):
    id: int
    section_name: str
    change_type: str
    original_text: str
    proposed_text: str
    rationale: str
    evidence_source: Optional[str]
    status: str
    user_override_text: Optional[str]

    class Config:
        from_attributes = True

class ChangeReviewAction(BaseModel):
    status: str # "Approved" | "Rejected" | "Edited"
    user_override_text: Optional[str] = None

class ATSAnalysisResponse(BaseModel):
    id: int
    ats_score: float
    keyword_coverage_pct: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    formatting_warnings: List[str]
    section_warnings: List[str]
    readability_score: float
    structural_analysis: Dict[str, Any]
    ai_suggestions: List[str]

    class Config:
        from_attributes = True

class CoverLetterResponse(BaseModel):
    id: int
    title: str
    content: str
    company_name: Optional[str]
    job_title: Optional[str]
    verified_claims_used: List[str]
    tone: str
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class CoverLetterUpdateRequest(BaseModel):
    content: str
    tone: Optional[str] = None
