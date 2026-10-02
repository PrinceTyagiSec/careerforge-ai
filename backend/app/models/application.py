import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True)
    tailored_resume_id = Column(Integer, ForeignKey("tailored_resumes.id", ondelete="SET NULL"), nullable=True)
    cover_letter_id = Column(Integer, ForeignKey("cover_letters.id", ondelete="SET NULL"), nullable=True)

    # Status: Interested, Saved, Applied, Assessment, Interview, Technical Interview, HR Interview, Offer, Rejected, Withdrawn, Closed
    status = Column(String(50), default="Applied", index=True)
    applied_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Reminders & Dates
    follow_up_date = Column(DateTime, nullable=True)
    interview_date = Column(DateTime, nullable=True)
    deadline_date = Column(DateTime, nullable=True)
    reminder_sent = Column(Boolean, default=False)
    
    # Details & Contacts
    contact_name = Column(String(200), nullable=True)
    contact_email = Column(String(200), nullable=True)
    salary_offered = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    outcome = Column(String(100), nullable=True) # Pending, Hired, Offer Declined, Rejected
    
    # Duplicate application check
    is_duplicate_warning_acknowledged = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    events = relationship("ApplicationEvent", back_populates="application", cascade="all, delete-orphan", order_by="ApplicationEvent.occurred_at.desc()")
    notes = relationship("ApplicationNote", back_populates="application", cascade="all, delete-orphan", order_by="ApplicationNote.created_at.desc()")


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False) # e.g. "Job saved", "Applied", "Interview scheduled", "Offer received"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    occurred_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("Application", back_populates="events")


class ApplicationNote(Base):
    __tablename__ = "application_notes"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("Application", back_populates="notes")
