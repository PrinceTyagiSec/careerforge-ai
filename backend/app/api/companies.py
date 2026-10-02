from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.user_helper import get_or_create_default_user
from app.models.job import Company, Job
from app.models.application import Application

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("")
def list_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).order_by(Company.name).all()
    results = []
    for c in companies:
        job_count = db.query(Job).filter(Job.company_id == c.id).count()
        results.append({
            "id": c.id,
            "name": c.name,
            "location": c.location,
            "industry": c.industry,
            "website": c.website,
            "rating": c.rating,
            "job_count": job_count
        })
    return results

@router.get("/{company_id}")
def get_company_detail(company_id: int, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    jobs = db.query(Job).filter(Job.company_id == company.id).order_by(desc(Job.discovered_at)).all()
    
    # User's previous interactions with this company
    job_ids = [j.id for j in jobs]
    user_apps = db.query(Application).filter(Application.user_id == user.id, Application.job_id.in_(job_ids)).all()

    return {
        "id": company.id,
        "name": company.name,
        "location": company.location,
        "industry": company.industry,
        "website": company.website,
        "description": company.description,
        "rating": company.rating,
        "available_job_count": len(jobs),
        "jobs": [{
            "id": j.id,
            "title": j.title,
            "location": j.location,
            "remote_status": j.remote_status,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
            "freshness_status": j.freshness_status
        } for j in jobs],
        "user_applications": [{
            "id": a.id,
            "job_id": a.job_id,
            "status": a.status,
            "applied_at": a.applied_at
        } for a in user_apps]
    }
