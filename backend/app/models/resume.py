import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filepath = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False) # pdf, docx, txt, md, image
    file_size_bytes = Column(Integer, default=0)
    raw_text = Column(Text, nullable=True)
    ocr_applied = Column(Boolean, default=False)
    ocr_confidence = Column(Float, nullable=True)
    parsing_status = Column(String(50), default="pending") # pending, parsed, failed
    parsing_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="resumes")
    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan")
    sections = relationship("ResumeSection", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="resume", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="resume", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="resume", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="resume", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="resume", cascade="all, delete-orphan")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, default=1)
    name = Column(String(100), default="Master Version")
    is_active = Column(Boolean, default=True)
    template_name = Column(String(50), default="ATS Simple") # ATS Simple, Modern, Technical, Software Engineer, Cybersecurity, Minimal, Academic
    custom_data_json = Column(Text, nullable=True) # Full snapshot of version data
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("Resume", back_populates="versions")
    tailored_resumes = relationship("TailoredResume", back_populates="resume_version")


class ResumeSection(Base):
    __tablename__ = "resume_sections"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    section_type = Column(String(50), nullable=False) # summary, skills, experience, education, projects, certifications, achievements, custom
    heading = Column(String(100), nullable=False)
    order_index = Column(Integer, default=0)
    content = Column(Text, nullable=True) # text or json payload
    is_enabled = Column(Boolean, default=True)

    resume = relationship("Resume", back_populates="sections")


class Claim(Base):
    """
    Atomic factual claim extracted from candidate resume or entered by user.
    Used for factual integrity protection and preventing AI hallucinations.
    """
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False) # skill, experience, metric, title, tool, education
    statement = Column(Text, nullable=False)
    source_section = Column(String(100), nullable=True) # e.g. "Experience -> Backend Engineer"
    source_snippet = Column(Text, nullable=True)
    verification_status = Column(String(50), default="Extracted") # Verified, User Provided, Extracted, AI Interpretation, Unverified
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("Resume", back_populates="claims")


class ResumeClaim(Base):
    __tablename__ = "resume_claims"

    id = Column(Integer, primary_key=True, index=True)
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id", ondelete="CASCADE"), nullable=False)
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    is_included = Column(Boolean, default=True)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    canonical_name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), default="Technical") # Technical, Tool, Soft, Framework, Cloud, Language
    years_experience = Column(Float, nullable=True)
    proficiency = Column(String(50), default="Intermediate") # Beginner, Intermediate, Advanced, Expert
    verification_status = Column(String(50), default="Verified")

    resume = relationship("Resume", back_populates="skills")


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    company = Column(String(200), nullable=False)
    title = Column(String(200), nullable=False)
    location = Column(String(150), nullable=True)
    employment_type = Column(String(50), default="Full-time") # Full-time, Internship, Contract
    start_date = Column(String(50), nullable=True) # "Jan 2023" or "2023-01"
    end_date = Column(String(50), nullable=True)
    is_current = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    bullets_json = Column(Text, default="[]") # JSON list of bullet points
    order_index = Column(Integer, default=0)

    resume = relationship("Resume", back_populates="experiences")


class Education(Base):
    __tablename__ = "educations"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(200), nullable=False)
    field_of_study = Column(String(200), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    grade = Column(String(50), nullable=True)
    order_index = Column(Integer, default=0)

    resume = relationship("Resume", back_populates="educations")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    role = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    technologies_json = Column(Text, default="[]") # list of tech
    url = Column(String(255), nullable=True)
    bullets_json = Column(Text, default="[]")
    order_index = Column(Integer, default=0)

    resume = relationship("Resume", back_populates="projects")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    issuing_organization = Column(String(255), nullable=False)
    issue_date = Column(String(50), nullable=True)
    expiration_date = Column(String(50), nullable=True)
    credential_url = Column(String(255), nullable=True)

    resume = relationship("Resume", back_populates="certifications")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(String(50), nullable=True)

    resume = relationship("Resume", back_populates="achievements")
