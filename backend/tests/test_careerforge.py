import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User, CandidateProfile
from app.models.job import Job, JobRequirement
from app.models.resume import Resume, Skill, Experience, Claim
from app.services.job_quality.normalizer import JobNormalizer
from app.services.job_quality.deduplicator import JobDeduplicator
from app.services.job_quality.freshness import FreshnessService
from app.services.matching.engine import MatchingEngine
from app.services.resume.quality_engine import ResumeQualityEngine
from app.services.resume.tailor_engine import TailoredResumeEngine
from app.services.job_providers.imported import UserImportProvider
from app.services.job_providers.manager import JobProviderManager

# Test SQLite in-memory DB
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_skill_normalization():
    # Canonical skill mappings
    canon, cat = JobNormalizer.normalize_skill("ts")
    assert canon == "TypeScript"
    assert cat == "Language"

    canon, cat = JobNormalizer.normalize_skill("postgres")
    assert canon == "PostgreSQL"
    assert cat == "Database"

    canon, cat = JobNormalizer.normalize_skill("fast api")
    assert canon == "FastAPI"
    assert cat == "Framework"

def test_location_and_salary_normalization():
    loc, city, state, remote = JobNormalizer.normalize_location("Bengaluru, India (Remote)")
    assert remote == "Remote"
    assert city == "Bengaluru"

    s_min, s_max, curr = JobNormalizer.normalize_salary(100000, 150000, "INR")
    # Converted from monthly to annual LPA
    assert s_min == 1200000.0
    assert s_max == 1800000.0

def test_job_deduplication(db):
    mgr = JobProviderManager(db)
    
    # Ingest job from Adzuna
    item1 = UserImportProvider.import_from_text(
        title="Senior Python Engineer",
        company_name="InnovateTech India",
        description="Looking for Python and FastAPI developers with 3 years experience.",
        location="Bengaluru",
        url="https://innovatetech.com/jobs/101"
    )
    job1 = mgr.ingest_provider_item(item1)
    assert job1 is not None

    # Ingest same job from Jooble with slight URL variation
    item2 = UserImportProvider.import_from_text(
        title="Senior Python Engineer",
        company_name="InnovateTech India",
        description="Looking for Python and FastAPI developers with 3 years experience.",
        location="Bengaluru",
        url="https://innovatetech.com/jobs/101?utm_source=jooble"
    )
    job2 = mgr.ingest_provider_item(item2)
    assert job2.id == job1.id # Deduplicated to single canonical job!
    assert len(job1.sources) >= 1

def test_freshness_status():
    now = datetime.datetime.utcnow()
    fresh = FreshnessService.calculate_freshness_status(published_at=now, discovered_at=now)
    assert fresh == "Fresh"

    old_date = now - datetime.timedelta(days=30)
    stale = FreshnessService.calculate_freshness_status(published_at=old_date, discovered_at=old_date)
    assert stale == "Possibly Stale"

def test_matching_engine_and_claim_protection(db):
    user = User(email="test@candidate.com", full_name="Arjun Sharma")
    db.add(user)
    db.flush()

    profile = CandidateProfile(
        user_id=user.id,
        headline="Python Backend Developer",
        location="Bengaluru, Karnataka",
        remote_preference="Flexible",
        years_of_experience=3.0
    )
    db.add(profile)

    resume = Resume(
        user_id=user.id,
        original_filename="arjun_resume.pdf",
        stored_filepath="dummy.pdf",
        file_type="pdf",
        raw_text="Experienced Python and FastAPI backend developer with 3 years experience building APIs."
    )
    db.add(resume)
    db.flush()

    sk1 = Skill(resume_id=resume.id, name="Python", canonical_name="Python", category="Language", proficiency="Advanced")
    sk2 = Skill(resume_id=resume.id, name="FastAPI", canonical_name="FastAPI", category="Framework", proficiency="Advanced")
    db.add_all([sk1, sk2])

    exp = Experience(
        resume_id=resume.id,
        company="Razorpay",
        title="Backend Developer",
        bullets_json='["Engineered high-throughput payments API using Python and FastAPI"]'
    )
    db.add(exp)
    db.commit()

    # Job requiring Python, FastAPI, and Kubernetes
    job = Job(
        title="Python Developer",
        normalized_title="Python Developer",
        company_name="Swiggy",
        normalized_company="swiggy",
        location="Bengaluru, Karnataka",
        remote_status="Remote",
        canonical_url="https://swiggy.com/jobs/99",
        dedup_hash="dummyhash",
        description="Requires Python, FastAPI, and Kubernetes."
    )
    db.add(job)
    db.flush()

    req1 = JobRequirement(job_id=job.id, category="Language", requirement_text="Python", canonical_term="Python")
    req2 = JobRequirement(job_id=job.id, category="Framework", requirement_text="FastAPI", canonical_term="FastAPI")
    req3 = JobRequirement(job_id=job.id, category="DevOps", requirement_text="Kubernetes", canonical_term="Kubernetes")
    db.add_all([req1, req2, req3])
    db.commit()

    matcher = MatchingEngine(db, user)
    match = matcher.match_job(job)

    assert match.overall_score > 60.0
    assert "Python" in match.matching_skills_json
    assert "FastAPI" in match.matching_skills_json
    assert "Kubernetes" in match.missing_skills_json

    # Test Tailoring Engine
    tailored = TailoredResumeEngine.tailor_resume_for_job(db, user, job, resume)
    assert tailored is not None
    assert len(tailored.changes) > 0

    # Test Quality Engine
    quality = ResumeQualityEngine.analyze(db, resume)
    assert quality["overall_quality_score"] > 0
