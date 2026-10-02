from app.core.database import Base
from app.models.user import User, CandidateProfile, JobPreference
from app.models.resume import (
    Resume, ResumeVersion, ResumeSection, Claim, ResumeClaim,
    Skill, Experience, Education, Project, Certification, Achievement
)
from app.models.job import Job, Company, JobSource, JobRequirement
from app.models.matching import JobMatch, MatchEvidence
from app.models.tailored import TailoredResume, TailoredChange, ATSAnalysis, CoverLetter
from app.models.application import Application, ApplicationEvent, ApplicationNote
from app.models.saved_search import SavedSearch
from app.models.telegram import TelegramIntegration, NotificationPreference, TelegramNotification
from app.models.system import ProviderCredential, ProviderHealth, BackgroundTask, AIConfiguration

__all__ = [
    "Base",
    "User",
    "CandidateProfile",
    "JobPreference",
    "Resume",
    "ResumeVersion",
    "ResumeSection",
    "Claim",
    "ResumeClaim",
    "Skill",
    "Experience",
    "Education",
    "Project",
    "Certification",
    "Achievement",
    "Job",
    "Company",
    "JobSource",
    "JobRequirement",
    "JobMatch",
    "MatchEvidence",
    "TailoredResume",
    "TailoredChange",
    "ATSAnalysis",
    "CoverLetter",
    "Application",
    "ApplicationEvent",
    "ApplicationNote",
    "SavedSearch",
    "TelegramIntegration",
    "NotificationPreference",
    "TelegramNotification",
    "ProviderCredential",
    "ProviderHealth",
    "BackgroundTask",
    "AIConfiguration",
]
