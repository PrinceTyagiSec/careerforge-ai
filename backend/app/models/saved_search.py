import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    keywords = Column(String(255), nullable=True)
    location = Column(String(255), default="Remote India")
    remote_preference = Column(String(50), default="Flexible") # Remote, Hybrid, On-site, Flexible
    min_salary = Column(Float, nullable=True)
    experience_level = Column(String(50), nullable=True) # 0-2 years, 3-5 years, etc.
    employment_type = Column(String(50), nullable=True) # Full-time, etc.
    freshness_days = Column(Integer, default=7)
    preferred_skills_json = Column(Text, default="[]")
    
    # Scheduling & Monitoring (Section 7 & 8)
    is_enabled = Column(Boolean, default=True)
    frequency_minutes = Column(Integer, default=360) # Default every 6 hours
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Stats
    total_found_count = Column(Integer, default=0)
    new_jobs_count = Column(Integer, default=0)
    high_match_count = Column(Integer, default=0)
    
    # Notifications
    notify_telegram = Column(Boolean, default=True)
    min_match_threshold = Column(Float, default=75.0)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="saved_searches")
