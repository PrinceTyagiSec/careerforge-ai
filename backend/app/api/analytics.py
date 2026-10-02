import json
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.user_helper import get_or_create_default_user
from app.models.job import Job, JobRequirement
from app.models.matching import JobMatch
from app.models.application import Application
from app.models.resume import Resume, Skill
from app.models.system import ProviderHealth, BackgroundTask
from app.services.resume.quality_engine import ResumeQualityEngine
from app.services.ai.ollama_client import OllamaClient

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)

    total_discovered = db.query(Job).count()
    total_saved = db.query(JobMatch).filter(JobMatch.user_id == user.id, JobMatch.is_saved == True).count()
    
    apps = db.query(Application).filter(Application.user_id == user.id).all()
    total_applied = len(apps)
    
    interviews_count = sum(1 for a in apps if "Interview" in a.status or a.interview_date is not None)
    offers_count = sum(1 for a in apps if a.status == "Offer")

    response_rate = round((interviews_count / total_applied * 100.0), 1) if total_applied > 0 else 0.0

    # Applications by status
    status_counts = Counter(a.status for a in apps)

    # Top skill gaps across all matching jobs
    all_matches = db.query(JobMatch).filter(JobMatch.user_id == user.id).all()
    missing_skill_counter = Counter()
    for m in all_matches:
        try:
            missing = json.loads(m.missing_skills_json or "[]")
            for sk in missing:
                missing_skill_counter[sk] += 1
        except Exception:
            pass

    top_skill_gaps = [{"skill": skill, "count": count} for skill, count in missing_skill_counter.most_common(6)]

    # Resume quality score
    resume = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).first()
    resume_quality = None
    if resume:
        analysis = ResumeQualityEngine.analyze(db, resume)
        resume_quality = analysis.get("overall_quality_score")

    # Telegram status
    tele_connected = bool(user.telegram_integration and user.telegram_integration.is_connected)

    # Ollama status
    ollama = OllamaClient()
    ollama_health = await ollama.check_health()

    # Provider health
    prov_health = db.query(ProviderHealth).all()

    return {
        "total_jobs_discovered": total_discovered,
        "total_jobs_saved": total_saved,
        "total_applied": total_applied,
        "total_interviews": interviews_count,
        "total_offers": offers_count,
        "response_rate_pct": response_rate,
        "applications_by_status": dict(status_counts),
        "top_skill_gaps": top_skill_gaps,
        "resume_quality_score": resume_quality,
        "telegram_connected": tele_connected,
        "ollama_status": ollama_health["status"],
        "provider_health": [{
            "provider_name": p.provider_name.capitalize(),
            "status": p.status,
            "last_checked_at": p.last_checked_at,
            "error_message": p.error_message
        } for p in prov_health]
    }

@router.get("/tasks")
def list_background_tasks(db: Session = Depends(get_db)):
    tasks = db.query(BackgroundTask).order_by(BackgroundTask.created_at.desc()).limit(20).all()
    return [{
        "id": t.id,
        "task_identifier": t.task_identifier,
        "task_name": t.task_name,
        "status": t.status,
        "started_at": t.started_at,
        "completed_at": t.completed_at,
        "retry_count": t.retry_count,
        "error_message": t.error_message,
        "result_summary": t.result_summary
    } for t in tasks]
