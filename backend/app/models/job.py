import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    normalized_name = Column(String(255), index=True, nullable=False)
    website = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    jobs = relationship("Job", back_populates="company_rel")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    normalized_title = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    normalized_company = Column(String(255), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)

    location = Column(String(255), default="India", index=True)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True)
    country = Column(String(50), default="India")
    remote_status = Column(String(50), default="On-site") # Remote, Hybrid, On-site

    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), default="INR")
    salary_period = Column(String(20), default="yearly") # yearly, monthly, hourly
    salary_is_predicted = Column(Boolean, default=False)

    employment_type = Column(String(50), default="Full-time") # Full-time, Contract, Internship, Part-time
    experience_min_years = Column(Float, nullable=True)
    experience_max_years = Column(Float, nullable=True)

    description = Column(Text, nullable=False)
    canonical_url = Column(String(1000), nullable=False, index=True)
    dedup_hash = Column(String(64), nullable=False, index=True) # Hash for fast deduplication

    # Freshness
    published_at = Column(DateTime, nullable=True)
    discovered_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_verified_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    freshness_status = Column(String(50), default="Fresh") # Fresh, Recently Updated, Possibly Stale, Expired, Unavailable
    is_active = Column(Boolean, default=True)

    # URL Validation
    is_url_valid = Column(Boolean, default=True)
    url_status_code = Column(Integer, nullable=True)

    # Metadata
    raw_payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    company_rel = relationship("Company", back_populates="jobs")
    sources = relationship("JobSource", back_populates="job", cascade="all, delete-orphan")
    requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job")

    __table_args__ = (
        Index("idx_job_company_title_loc", "normalized_company", "normalized_title", "location"),
    )


class JobSource(Base):
    """
    Source attribution for a job (e.g. Adzuna, Jooble, User Import).
    Supports multiple sources for the same deduplicated job.
    """
    __tablename__ = "job_sources"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    provider_name = Column(String(100), nullable=False) # Adzuna, Jooble, User Import, Manual Entry, URL Scrape
    external_id = Column(String(255), nullable=True)
    source_url = Column(String(1000), nullable=False)
    raw_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("Job", back_populates="sources")


class JobRequirement(Base):
    """
    Structured extracted requirements for matching.
    """
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False) # Skill, Experience, Education, Certification, Tool
    requirement_text = Column(String(255), nullable=False)
    canonical_term = Column(String(100), nullable=False, index=True)
    is_mandatory = Column(Boolean, default=True)
    min_years = Column(Float, nullable=True)
    importance_weight = Column(Float, default=1.0)

    job = relationship("Job", back_populates="requirements")
