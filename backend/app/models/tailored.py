import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class TailoredResume(Base):
    __tablename__ = "tailored_resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    target_role = Column(String(255), nullable=False)
    tailored_content_json = Column(Text, nullable=False) # structured snapshot of resume sections
    template_name = Column(String(50), default="ATS Simple")
    status = Column(String(50), default="Draft") # Draft, In Review, Approved, Exported
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    resume_version = relationship("ResumeVersion", back_populates="tailored_resumes")
    changes = relationship("TailoredChange", back_populates="tailored_resume", cascade="all, delete-orphan")
    ats_analyses = relationship("ATSAnalysis", back_populates="tailored_resume", cascade="all, delete-orphan")


class TailoredChange(Base):
    """
    Every single modification made to a tailored resume must be recorded here.
    Supports Human Review: user can approve, reject, or edit each change.
    """
    __tablename__ = "tailored_changes"

    id = Column(Integer, primary_key=True, index=True)
    tailored_resume_id = Column(Integer, ForeignKey("tailored_resumes.id", ondelete="CASCADE"), nullable=False)
    section_name = Column(String(100), nullable=False)
    change_type = Column(String(50), nullable=False) # Rewrite, Reorder, Emphasize, Keyword Align, Summary Adjust
    original_text = Column(Text, nullable=False)
    proposed_text = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    evidence_source = Column(String(255), nullable=True) # traceable candidate claim
    status = Column(String(50), default="Pending") # Pending, Approved, Rejected, Edited
    user_override_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    tailored_resume = relationship("TailoredResume", back_populates="changes")


class ATSAnalysis(Base):
    """
    Dedicated ATS and structural quality analysis.
    Clearly separates deterministic ATS structural analysis from AI suggestions.
    """
    __tablename__ = "ats_analyses"

    id = Column(Integer, primary_key=True, index=True)
    tailored_resume_id = Column(Integer, ForeignKey("tailored_resumes.id", ondelete="CASCADE"), nullable=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True)

    ats_score = Column(Float, nullable=False) # 0 to 100
    keyword_coverage_pct = Column(Float, default=0.0)
    matched_keywords_json = Column(Text, default="[]")
    missing_keywords_json = Column(Text, default="[]")
    
    formatting_warnings_json = Column(Text, default="[]") # parsing risks, table usage, symbols
    section_warnings_json = Column(Text, default="[]") # missing standard headings
    readability_score = Column(Float, default=100.0)
    structural_analysis_json = Column(Text, default="{}") # deterministic analysis
    ai_suggestions_json = Column(Text, default="[]") # non-mandatory AI tips
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    tailored_resume = relationship("TailoredResume", back_populates="ats_analyses")


class CoverLetter(Base):
    """
    Job-specific cover letter generated strictly from verified candidate information.
    """
    __tablename__ = "cover_letters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    verified_claims_used_json = Column(Text, default="[]") # Traceable claims used
    tone = Column(String(50), default="Professional & Direct")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
