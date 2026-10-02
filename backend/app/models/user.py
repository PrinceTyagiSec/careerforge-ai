import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    profile = relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    job_preferences = relationship("JobPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    saved_searches = relationship("SavedSearch", back_populates="user", cascade="all, delete-orphan")
    telegram_integration = relationship("TelegramIntegration", back_populates="user", uselist=False, cascade="all, delete-orphan")


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    headline = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    location = Column(String(255), default="India")
    remote_preference = Column(String(50), default="Flexible") # Remote, Hybrid, On-site, Flexible
    target_role = Column(String(255), nullable=True)
    expected_salary_min = Column(Float, nullable=True)
    expected_salary_max = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    years_of_experience = Column(Float, default=0.0)
    availability = Column(String(100), default="Immediate / 30 Days")
    work_authorization = Column(String(255), default="Authorized to work in India")
    github_url = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    portfolio_url = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")


class JobPreference(Base):
    __tablename__ = "job_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    preferred_roles = Column(Text, default="[]") # JSON list of strings
    preferred_locations = Column(Text, default="[\"Remote India\", \"Bengaluru\", \"Noida\", \"Gurgaon\", \"Hyderabad\", \"Pune\", \"Mumbai\"]")
    preferred_skills = Column(Text, default="[]")
    excluded_companies = Column(Text, default="[]")
    min_salary = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    remote_only = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="job_preferences")
