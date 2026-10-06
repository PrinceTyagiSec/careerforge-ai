import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc

from app.core.database import get_db
from app.core.user_helper import get_or_create_default_user
from app.models.job import Job, JobSource, JobRequirement, Company
from app.models.matching import JobMatch, MatchEvidence
from app.models.resume import Resume
from app.models.tailored import TailoredResume, TailoredChange, ATSAnalysis, CoverLetter
from app.models.application import Application
from app.schemas.job import JobSearchFilter, JobImportRequest
from app.schemas.tailored import ChangeReviewAction, CoverLetterUpdateRequest
from app.services.job_providers.manager import JobProviderManager
from app.services.job_providers.imported import UserImportProvider
from app.services.matching.engine import MatchingEngine
from app.services.resume.tailor_engine import TailoredResumeEngine
from app.services.job_quality.freshness import FreshnessService

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/search-live")
async def search_live_jobs(
    keywords: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    remote_status: Optional[str] = Query(None),
    min_salary: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    """
    Query external job providers using explicit All Jobs filters first.
    If a filter is not provided, fall back to Candidate Profile / Market Preferences.
    """

    user = get_or_create_default_user(db)

    profile = user.profile
    preferences = user.job_preferences

    # ---------------------------------------------------------
    # Build effective provider query.
    #
    # Explicit All Jobs filters ALWAYS win.
    # Profile/preferences are only defaults for live discovery.
    # ---------------------------------------------------------

    effective_keywords = (
        keywords.strip()
        if keywords and keywords.strip()
        else None
    )

    # Provider keyword fallback priority:
    # 1. Explicit All Jobs keyword
    # 2. Candidate Profile target role
    # 3. Candidate Profile headline
    # 4. Market Preferences preferred role
    # 5. Safe default

    if not effective_keywords and profile:
        effective_keywords = (
            profile.headline
            or profile.target_role
        )

    if not effective_keywords and preferences and preferences.preferred_roles:
        try:
            preferred_roles = json.loads(
                preferences.preferred_roles or "[]"
            )
        except Exception:
            preferred_roles = []

        if preferred_roles:
            effective_keywords = preferred_roles[0]

    if not effective_keywords:
        effective_keywords = "Software Engineer"

    # 2. Location
    effective_location = (
        location.strip()
        if location and location.strip()
        else None
    )

    if effective_location and effective_location.lower() == "all":
        effective_location = None

    if not effective_location and profile:
        effective_location = profile.location

    if effective_location and effective_location.lower() == "all":
        effective_location = None

    # 3. Remote preference
    effective_remote_status = (
        remote_status.strip()
        if remote_status
        and remote_status.strip()
        and remote_status.lower() != "all"
        else None
    )

    if not effective_remote_status and profile:
        if profile.remote_preference in {
            "Remote",
            "Hybrid",
            "On-site"
        }:
            effective_remote_status = profile.remote_preference

    if not effective_remote_status and preferences:
        if preferences.remote_only:
            effective_remote_status = "Remote"

    # 4. Salary
    effective_min_salary = min_salary

    if effective_min_salary is None and preferences:
        effective_min_salary = preferences.min_salary

    if effective_min_salary is None and profile:
        effective_min_salary = profile.expected_salary_min

    # ---------------------------------------------------------
    # DEBUG
    # ---------------------------------------------------------

    print("\n========== LIVE SEARCH EFFECTIVE QUERY ==========")
    print("explicit keywords :", keywords)
    print("explicit location :", location)
    print("profile headline  :", profile.headline if profile else None)
    print("profile target    :", profile.target_role if profile else None)
    print("profile location  :", profile.location if profile else None)
    print("effective keywords:", effective_keywords)
    print("effective location:", effective_location)
    print("effective remote  :", effective_remote_status)
    print("effective salary  :", effective_min_salary)
    print("=================================================\n")

    # ---------------------------------------------------------
    # Query external providers
    # ---------------------------------------------------------

    mgr = JobProviderManager(db)

    saved_jobs = await mgr.search_and_ingest(
        keywords=effective_keywords,
        location=effective_location,
        remote_status=effective_remote_status,
        min_salary=effective_min_salary,
        page=page,
        results_per_page=20
    )

    # Calculate match for user
    matcher = MatchingEngine(db, user)

    results = []

    for job in saved_jobs:
        match = matcher.match_job(job)

        results.append({
            "id": job.id,
            "title": job.title,
            "company_name": job.company_name,
            "location": job.location,
            "city": job.city,
            "remote_status": job.remote_status,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "freshness_status": job.freshness_status,
            "canonical_url": job.canonical_url,
            "match_score": match.overall_score,
            "matching_skills": json.loads(
                match.matching_skills_json or "[]"
            ),
            "missing_skills": json.loads(
                match.missing_skills_json or "[]"
            ),
            "sources": [
                {
                    "provider_name": s.provider_name,
                    "source_url": s.source_url
                }
                for s in job.sources
            ],
            "published_at": job.published_at
        })

    # Sort by match score descending
    results.sort(
        key=lambda x: x["match_score"] or 0,
        reverse=True
    )

    return {
        "count": len(results),
        "page": page,
        "results": results
    }

@router.post("/import")
async def import_job(data: JobImportRequest, db: Session = Depends(get_db)):
    """
    Imports a job from pasted description or live URL (Section 3.3).
    All imported jobs enter the exact same normalization, deduplication, and matching pipeline.
    """
    user = get_or_create_default_user(db)
    mgr = JobProviderManager(db)

    if data.import_type == "url":
        if not data.url:
            raise HTTPException(status_code=400, detail="URL is required for URL import")
        try:
            item = await UserImportProvider.import_from_url(data.url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch job from URL: {str(e)}")
    else:
        if not data.description:
            raise HTTPException(status_code=400, detail="Description is required for text import")
        item = UserImportProvider.import_from_text(
            title=data.title or "Imported Software Role",
            company_name=data.company_name or "Direct Employer",
            description=data.description,
            location=data.location or "India",
            salary_min=data.salary_min,
            salary_max=data.salary_max,
            url=data.url
        )

    job = mgr.ingest_provider_item(item)
    if not job:
        raise HTTPException(status_code=500, detail="Failed to process imported job")

    matcher = MatchingEngine(db, user)
    match = matcher.match_job(job)

    return {
        "message": "Job imported successfully",
        "job_id": job.id,
        "title": job.title,
        "company": job.company_name,
        "match_score": match.overall_score
    }

@router.get("")
def list_jobs(
    keywords: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    remote_status: Optional[str] = Query(None),
    min_salary: Optional[float] = Query(None),
    experience: Optional[str] = Query(None),
    freshness: Optional[str] = Query(None),
    min_match: Optional[float] = Query(None),
    saved_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    user = get_or_create_default_user(db)
    query = db.query(Job)

    if keywords:
        kw = f"%{keywords}%"
        query = query.filter(or_(Job.title.ilike(kw), Job.company_name.ilike(kw), Job.description.ilike(kw)))

    if location and location.lower() != "all":
        normalized_location = location.strip().lower()

        if normalized_location == "remote india":
            query = query.filter(
                and_(
                    func.lower(Job.remote_status) == "remote",
                    func.lower(Job.country) == "india"
                )
            )

        elif normalized_location in {"noida", "noida / ncr"}:
            query = query.filter(
                or_(
                    Job.location.ilike("%noida%"),
                    Job.city.ilike("%noida%"),
                    Job.location.ilike("%ncr%"),
                    Job.city.ilike("%ncr%")
                )
            )

        else:
            query = query.filter(
                Job.location.ilike(f"%{location}%")
            )

    if remote_status and remote_status.lower() != "all":
        query = query.filter(
            func.lower(Job.remote_status) == remote_status.strip().lower()
        )

    if min_salary:
        query = query.filter(or_(Job.salary_min >= min_salary, Job.salary_max >= min_salary))

    # Experience requirement filter
    if experience and experience.lower() != "all":
        experience_key = experience.strip().lower()

        if experience_key == "0-1":
            query = query.filter(
                Job.experience_min_years <= 1,
                Job.experience_max_years >= 0
            )

        elif experience_key == "1-3":
            query = query.filter(
                Job.experience_min_years <= 3,
                Job.experience_max_years >= 1
            )

        elif experience_key == "3-5":
            query = query.filter(
                Job.experience_min_years <= 5,
                Job.experience_max_years >= 3
            )

        elif experience_key == "5-8":
            query = query.filter(
                Job.experience_min_years <= 8,
                Job.experience_max_years >= 5
            )

        elif experience_key == "8+":
            query = query.filter(
                Job.experience_max_years >= 8
            )


    if freshness and freshness.lower() != "all":
        query = query.filter(
            func.lower(Job.freshness_status) == freshness.strip().lower()
        )

    jobs = query.order_by(desc(Job.discovered_at)).all()

    # Join matches for current user
    results = []
    matcher = MatchingEngine(db, user)

    for job in jobs:
        match = db.query(JobMatch).filter(JobMatch.user_id == user.id, JobMatch.job_id == job.id).first()
        if not match:
            match = matcher.match_job(job)

        if saved_only and not match.is_saved:
            continue

        if min_match and match.overall_score < min_match:
            continue

        app = db.query(Application).filter(Application.user_id == user.id, Application.job_id == job.id).first()

        results.append({
            "id": job.id,
            "title": job.title,
            "company_name": job.company_name,
            "location": job.location,
            "city": job.city,
            "remote_status": job.remote_status,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "freshness_status": job.freshness_status,
            "is_url_valid": job.is_url_valid,
            "canonical_url": job.canonical_url,
            "match_score": match.overall_score,
            "matching_skills": json.loads(match.matching_skills_json or "[]"),
            "missing_skills": json.loads(match.missing_skills_json or "[]"),
            "is_saved": match.is_saved,
            "application_status": app.status if app else None,
            "sources": [{"provider_name": s.provider_name, "source_url": s.source_url} for s in job.sources],
            "published_at": job.published_at,
            "discovered_at": job.discovered_at
        })

    # Pagination
    total = len(results)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated = results[start_idx:end_idx]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": paginated
    }

@router.get("/{job_id}")
def get_job_detail(job_id: int, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    matcher = MatchingEngine(db, user)
    match = db.query(JobMatch).filter(JobMatch.user_id == user.id, JobMatch.job_id == job.id).first()
    if not match:
        match = matcher.match_job(job)

    evidence_items = db.query(MatchEvidence).filter(MatchEvidence.job_match_id == match.id).all()
    reqs = db.query(JobRequirement).filter(JobRequirement.job_id == job.id).all()
    sources = db.query(JobSource).filter(JobSource.job_id == job.id).all()
    app = db.query(Application).filter(Application.user_id == user.id, Application.job_id == job.id).first()

    return {
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "location": job.location,
        "city": job.city,
        "state": job.state,
        "remote_status": job.remote_status,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "salary_currency": job.salary_currency,
        "employment_type": job.employment_type,
        "experience_min_years": job.experience_min_years,
        "experience_max_years": job.experience_max_years,
        "description": job.description,
        "canonical_url": job.canonical_url,
        "freshness_status": job.freshness_status,
        "is_url_valid": job.is_url_valid,
        "published_at": job.published_at,
        "discovered_at": job.discovered_at,
        "sources": [{"id": s.id, "provider_name": s.provider_name, "source_url": s.source_url} for s in sources],
        "requirements": [{"id": r.id, "category": r.category, "text": r.requirement_text, "canonical": r.canonical_term} for r in reqs],
        "match": {
            "overall_score": match.overall_score,
            "deterministic_score": match.deterministic_score,
            "skill_score": match.skill_score,
            "experience_score": match.experience_score,
            "location_score": match.location_score,
            "salary_score": match.salary_score,
            "matching_skills": json.loads(match.matching_skills_json or "[]"),
            "partial_skills": json.loads(match.partial_skills_json or "[]"),
            "missing_skills": json.loads(match.missing_skills_json or "[]"),
            "transferable_skills": json.loads(match.transferable_skills_json or "[]"),
            "explanation_summary": match.explanation_summary,
            "gap_analysis": json.loads(match.gap_analysis_json or "{}"),
            "is_saved": match.is_saved
        },
        "evidence": [{
            "id": e.id,
            "requirement_term": e.requirement_term,
            "match_status": e.match_status,
            "candidate_claim": e.candidate_claim,
            "source_reference": e.source_reference,
            "confidence": e.confidence,
            "verification_status": e.verification_status
        } for e in evidence_items],
        "application_status": app.status if app else None,
        "application_id": app.id if app else None
    }

@router.post("/{job_id}/toggle-save")
def toggle_save_job(job_id: int, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    matcher = MatchingEngine(db, user)
    match = db.query(JobMatch).filter(JobMatch.user_id == user.id, JobMatch.job_id == job_id).first()
    if not match:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        match = matcher.match_job(job)

    match.is_saved = not match.is_saved
    match.user_action = "saved" if match.is_saved else "none"
    db.commit()
    return {"job_id": job_id, "is_saved": match.is_saved}

@router.post("/{job_id}/tailor")
def tailor_resume_for_job(job_id: int, template: str = Query("ATS Simple"), db: Session = Depends(get_db)):
    """
    Generates a tailored resume with zero hallucination and human-reviewable change set (Section 21).
    """
    user = get_or_create_default_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).first()
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload a resume first before tailoring.")

    tailored = TailoredResumeEngine.tailor_resume_for_job(db, user, job, resume, template)
    changes = db.query(TailoredChange).filter(TailoredChange.tailored_resume_id == tailored.id).all()
    ats = db.query(ATSAnalysis).filter(ATSAnalysis.tailored_resume_id == tailored.id).first()
    cover_letter = db.query(CoverLetter).filter(CoverLetter.user_id == user.id, CoverLetter.job_id == job.id).first()

    return {
        "tailored_id": tailored.id,
        "job_id": job.id,
        "title": tailored.title,
        "status": tailored.status,
        "template_name": tailored.template_name,
        "content": json.loads(tailored.tailored_content_json),
        "changes": [{
            "id": c.id,
            "section_name": c.section_name,
            "change_type": c.change_type,
            "original_text": c.original_text,
            "proposed_text": c.proposed_text,
            "rationale": c.rationale,
            "evidence_source": c.evidence_source,
            "status": c.status,
            "user_override_text": c.user_override_text
        } for c in changes],
        "ats_analysis": {
            "score": ats.ats_score if ats else 85.0,
            "keyword_coverage_pct": ats.keyword_coverage_pct if ats else 80.0,
            "matched_keywords": json.loads(ats.matched_keywords_json or "[]") if ats else [],
            "missing_keywords": json.loads(ats.missing_keywords_json or "[]") if ats else [],
            "ai_suggestions": json.loads(ats.ai_suggestions_json or "[]") if ats else []
        },
        "cover_letter": {
            "id": cover_letter.id if cover_letter else None,
            "content": cover_letter.content if cover_letter else "",
            "verified_claims_used": json.loads(cover_letter.verified_claims_used_json or "[]") if cover_letter else []
        }
    }

@router.put("/{job_id}/tailor/changes/{change_id}")
def review_tailored_change(job_id: int, change_id: int, action: ChangeReviewAction, db: Session = Depends(get_db)):
    """
    Human Review (Section 23): Approve, Reject, or Edit proposed AI changes.
    """
    change = db.query(TailoredChange).filter(TailoredChange.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Tailored change not found")

    change.status = action.status
    if action.user_override_text is not None:
        change.user_override_text = action.user_override_text

    db.commit()
    return {"message": "Change updated", "change_id": change_id, "status": change.status}

@router.get("/{job_id}/cover-letter")
def get_cover_letter(job_id: int, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    cl = db.query(CoverLetter).filter(CoverLetter.user_id == user.id, CoverLetter.job_id == job_id).first()
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not generated yet. Tailor resume first.")

    return {
        "id": cl.id,
        "title": cl.title,
        "content": cl.content,
        "company_name": cl.company_name,
        "job_title": cl.job_title,
        "verified_claims_used": json.loads(cl.verified_claims_used_json or "[]"),
        "tone": cl.tone
    }

@router.put("/{job_id}/cover-letter")
def update_cover_letter(job_id: int, data: CoverLetterUpdateRequest, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    cl = db.query(CoverLetter).filter(CoverLetter.user_id == user.id, CoverLetter.job_id == job_id).first()
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")

    cl.content = data.content
    if data.tone:
        cl.tone = data.tone
    db.commit()
    return {"message": "Cover letter updated successfully"}
