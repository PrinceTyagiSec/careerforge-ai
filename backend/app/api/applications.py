import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.user_helper import get_or_create_default_user
from app.models.application import Application, ApplicationEvent, ApplicationNote
from app.models.job import Job, JobSource
from app.schemas.application import (
    ApplicationCreateRequest, ApplicationStatusUpdateRequest,
    ApplicationResponse, ApplicationEventResponse, ApplicationNoteResponse
)

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.get("")
def list_applications(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    apps = db.query(Application).filter(Application.user_id == user.id).order_by(desc(Application.updated_at)).all()
    results = []
    for a in apps:
        job = a.job
        results.append({
            "id": a.id,
            "job_id": a.job_id,
            "job_title": job.title if job else "Unknown Role",
            "company_name": job.company_name if job else "Unknown Company",
            "location": job.location if job else "India",
            "status": a.status,
            "applied_at": a.applied_at,
            "follow_up_date": a.follow_up_date,
            "interview_date": a.interview_date,
            "deadline_date": a.deadline_date,
            "salary_offered": a.salary_offered,
            "outcome": a.outcome,
            "events_count": len(a.events),
            "notes_count": len(a.notes)
        })
    return results

@router.post("")
def create_application(data: ApplicationCreateRequest, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Section 52: Duplicate Application Protection
    # Check if user already applied to this job or an identical underlying job
    existing_direct = db.query(Application).filter(
        Application.user_id == user.id,
        Application.job_id == job.id
    ).first()

    if existing_direct:
        return {
            "duplicate_warning": True,
            "application_id": existing_direct.id,
            "message": f"You already have an active application for this exact role (Status: {existing_direct.status})."
        }

    # Check for identical company and title applied elsewhere
    similar_app = db.query(Application).join(Job).filter(
        Application.user_id == user.id,
        Job.normalized_company == job.normalized_company,
        Job.normalized_title == job.normalized_title
    ).first()

    if similar_app and not data.acknowledge_duplicate:
        return {
            "duplicate_warning": True,
            "existing_company": job.company_name,
            "existing_title": job.title,
            "existing_app_id": similar_app.id,
            "message": f"Duplicate Application Warning: You previously applied to '{similar_app.job.title}' at '{similar_app.job.company_name}'. Please confirm if you wish to apply again."
        }

    app = Application(
        user_id=user.id,
        job_id=job.id,
        status=data.status or "Applied",
        applied_at=data.applied_at or datetime.datetime.utcnow(),
        follow_up_date=data.follow_up_date,
        interview_date=data.interview_date,
        deadline_date=data.deadline_date,
        contact_name=data.contact_name,
        contact_email=data.contact_email,
        salary_offered=data.salary_offered,
        is_duplicate_warning_acknowledged=data.acknowledge_duplicate
    )
    db.add(app)
    db.flush()

    # Create Initial Event (Section 29)
    event = ApplicationEvent(
        application_id=app.id,
        event_type="Applied",
        title="Application Submitted",
        description=f"Applied to {job.title} at {job.company_name}."
    )
    db.add(event)

    if data.notes:
        note = ApplicationNote(
            application_id=app.id,
            content=data.notes
        )
        db.add(note)

    db.commit()
    db.refresh(app)
    return {"message": "Application created successfully", "application_id": app.id, "duplicate_warning": False}

@router.get("/{app_id}")
def get_application_detail(app_id: int, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    job = app.job
    return {
        "id": app.id,
        "job_id": app.job_id,
        "job_title": job.title if job else "",
        "company_name": job.company_name if job else "",
        "location": job.location if job else "",
        "status": app.status,
        "applied_at": app.applied_at,
        "follow_up_date": app.follow_up_date,
        "interview_date": app.interview_date,
        "deadline_date": app.deadline_date,
        "contact_name": app.contact_name,
        "contact_email": app.contact_email,
        "salary_offered": app.salary_offered,
        "outcome": app.outcome,
        "events": [{
            "id": ev.id,
            "event_type": ev.event_type,
            "title": ev.title,
            "description": ev.description,
            "occurred_at": ev.occurred_at
        } for ev in app.events],
        "notes": [{
            "id": n.id,
            "content": n.content,
            "created_at": n.created_at
        } for n in app.notes]
    }

@router.put("/{app_id}/status")
def update_application_status(app_id: int, data: ApplicationStatusUpdateRequest, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    old_status = app.status
    app.status = data.status
    if data.follow_up_date:
        app.follow_up_date = data.follow_up_date
    if data.interview_date:
        app.interview_date = data.interview_date
    if data.salary_offered:
        app.salary_offered = data.salary_offered
    if data.outcome:
        app.outcome = data.outcome

    # Timeline event
    title = data.event_title or f"Status changed to {data.status}"
    desc = data.event_description or f"Progressed from {old_status} to {data.status}."
    event = ApplicationEvent(
        application_id=app.id,
        event_type=data.status,
        title=title,
        description=desc
    )
    db.add(event)
    db.commit()
    return {"message": "Application status updated", "new_status": app.status}

@router.post("/{app_id}/notes")
def add_application_note(app_id: int, content: str, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    note = ApplicationNote(application_id=app.id, content=content)
    db.add(note)
    db.commit()
    return {"message": "Note added", "note_id": note.id}
