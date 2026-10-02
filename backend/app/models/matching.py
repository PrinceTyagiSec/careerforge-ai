import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    # Scores (0.0 to 100.0)
    overall_score = Column(Float, nullable=False, index=True)
    deterministic_score = Column(Float, nullable=False)
    semantic_score = Column(Float, default=0.0)
    skill_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    salary_score = Column(Float, default=0.0)
    
    # Categorized breakdown
    matching_skills_json = Column(Text, default="[]")
    partial_skills_json = Column(Text, default="[]")
    missing_skills_json = Column(Text, default="[]")
    transferable_skills_json = Column(Text, default="[]")
    
    # Detailed explanation & gap breakdown
    explanation_summary = Column(Text, nullable=True)
    gap_analysis_json = Column(Text, default="{}")
    
    # User interaction signals for personalized ranking (Section 17)
    user_action = Column(String(50), default="none") # none, saved, applied, rejected, ignored, hidden
    is_saved = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)
    
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="matches")
    evidence_items = relationship("MatchEvidence", back_populates="job_match", cascade="all, delete-orphan")


class MatchEvidence(Base):
    """
    Traceable evidence proving why candidate meets or misses a requirement.
    Ensures AI never manufactures match proof.
    """
    __tablename__ = "match_evidence"

    id = Column(Integer, primary_key=True, index=True)
    job_match_id = Column(Integer, ForeignKey("job_matches.id", ondelete="CASCADE"), nullable=False)
    requirement_term = Column(String(100), nullable=False)
    match_status = Column(String(50), default="Strong") # Strong, Partial, Missing, Transferable
    candidate_claim = Column(Text, nullable=True)
    source_reference = Column(String(255), nullable=True) # e.g. "Resume -> Experience -> Company X -> Bullet 2"
    confidence = Column(Float, default=1.0)
    verification_status = Column(String(50), default="Verified") # Verified, User Provided, Extracted, AI Interpretation

    job_match = relationship("JobMatch", back_populates="evidence_items")
