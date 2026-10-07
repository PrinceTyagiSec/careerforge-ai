import os
import shutil
import json
import uuid
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import UPLOADS_DIR, EXPORTS_DIR
from app.core.user_helper import get_or_create_default_user
from app.models.resume import (
    Resume, ResumeVersion, ResumeSection, Claim, Skill,
    Experience, Education, Project, Certification, Achievement
)
from app.services.resume.extractor import ResumeExtractor
from app.services.resume.parser import ResumeParser
from app.services.resume.quality_engine import ResumeQualityEngine
from app.services.resume.exporter import ResumeExporter

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = get_or_create_default_user(db)
    
    # Save uploaded file safely
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"resume_{uuid.uuid4().hex[:8]}_{file.filename}"
    save_path = UPLOADS_DIR / unique_filename

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(save_path)

    # Step 1: Text extraction + OCR fallback
    raw_text, ocr_applied, ocr_conf, ocr_err = ResumeExtractor.extract_from_file(str(save_path), file.filename)

    resume = Resume(
        user_id=user.id,
        original_filename=file.filename,
        stored_filepath=str(save_path),
        file_type=file_ext.lstrip("."),
        file_size_bytes=file_size,
        raw_text=raw_text,
        ocr_applied=ocr_applied,
        ocr_confidence=ocr_conf,
        parsing_status="pending"
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Step 2: Deterministic Entity, Section, and Claim Parsing
    parse_result = ResumeParser.parse_and_populate(db, resume, user)

    return {
        "resume_id": resume.id,
        "filename": resume.original_filename,
        "file_type": resume.file_type,
        "ocr_applied": ocr_applied,
        "ocr_confidence": ocr_conf,
        "parsing_status": resume.parsing_status,
        "extracted_summary": parse_result
    }

@router.get("")
def list_resumes(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    resumes = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).all()
    results = []
    for r in resumes:
        skills_count = db.query(Skill).filter(Skill.resume_id == r.id).count()
        results.append({
            "id": r.id,
            "original_filename": r.original_filename,
            "file_type": r.file_type,
            "ocr_applied": r.ocr_applied,
            "parsing_status": r.parsing_status,
            "skills_count": skills_count,
            "created_at": r.created_at
        })
    return results

@router.get("/{resume_id}")
def get_resume_detail(resume_id: int, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    skills = db.query(Skill).filter(Skill.resume_id == resume.id).all()
    experiences = db.query(Experience).filter(Experience.resume_id == resume.id).order_by(Experience.order_index).all()
    educations = db.query(Education).filter(Education.resume_id == resume.id).order_by(Education.order_index).all()
    projects = db.query(Project).filter(Project.resume_id == resume.id).order_by(Project.order_index).all()
    sections = db.query(ResumeSection).filter(ResumeSection.resume_id == resume.id).order_by(ResumeSection.order_index).all()
    claims = db.query(Claim).filter(Claim.resume_id == resume.id).all()

    return {
        "id": resume.id,
        "original_filename": resume.original_filename,
        "file_type": resume.file_type,
        "raw_text": resume.raw_text,
        "ocr_applied": resume.ocr_applied,
        "ocr_confidence": resume.ocr_confidence,
        "parsing_status": resume.parsing_status,
        "skills": [{"id": s.id, "name": s.name, "canonical_name": s.canonical_name, "category": s.category, "proficiency": s.proficiency} for s in skills],
        "experiences": [{
            "id": e.id, "company": e.company, "title": e.title, "location": e.location,
            "start_date": e.start_date, "end_date": e.end_date, "is_current": e.is_current,
            "bullets": json.loads(e.bullets_json or "[]")
        } for e in experiences],
        "educations": [{
            "id": ed.id, "institution": ed.institution, "degree": ed.degree,
            "field_of_study": ed.field_of_study, "start_date": ed.start_date, "end_date": ed.end_date
        } for ed in educations],
        "projects": [{
            "id": p.id, "title": p.title, "description": p.description,
            "bullets": json.loads(p.bullets_json or "[]")
        } for p in projects],
        "certifications": [
    {
        "id": certification.id,
        "name": certification.name,
        "issuing_organization": certification.issuing_organization,
        "issue_date": certification.issue_date,
        "expiration_date": certification.expiration_date,
        "credential_url": certification.credential_url,
    }
    for certification in resume.certifications
],
"achievements": [
    {
        "id": achievement.id,
        "title": achievement.title,
        "description": achievement.description,
        "date": achievement.date,
    }
    for achievement in resume.achievements
],
        "sections": [{
            "id": sec.id, "section_type": sec.section_type, "heading": sec.heading,
            "order_index": sec.order_index, "content": sec.content, "is_enabled": sec.is_enabled
        } for sec in sections],
        "claims": [{
            "id": c.id, "category": c.category, "statement": c.statement,
            "source_section": c.source_section, "verification_status": c.verification_status,
            "confidence": c.confidence
        } for c in claims]
    }

@router.get("/{resume_id}/quality")
def get_resume_quality(resume_id: int, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    analysis = ResumeQualityEngine.analyze(db, resume)
    return analysis

@router.post("/{resume_id}/reparse")
def reparse_resume(resume_id: int, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    res = ResumeParser.parse_and_populate(db, resume, user)
    return {"message": "Resume successfully re-parsed", "summary": res}

@router.get("/{resume_id}/export")
def export_resume(
    resume_id: int,
    format: str = Query("pdf", pattern="^(pdf|docx|md|txt)$"),
    template: str = Query("ATS Simple"),
    db: Session = Depends(get_db)
):
    user = get_or_create_default_user(db)
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Build data dictionary
    skills = db.query(Skill).filter(Skill.resume_id == resume.id).all()
    experiences = db.query(Experience).filter(Experience.resume_id == resume.id).order_by(Experience.order_index).all()
    educations = db.query(Education).filter(Education.resume_id == resume.id).order_by(Education.order_index).all()
    projects = db.query(Project).filter(Project.resume_id == resume.id).order_by(Project.order_index).all()

    profile = user.profile
    data = {
        "candidate_name": user.full_name or "Candidate",
        "headline": profile.headline if profile else "Software Developer",
        "email": user.email,
        "phone": profile.phone if profile else "",
        "location": profile.location if profile else "India",
        "summary": profile.summary if profile else "",
        "skills": [{"name": s.name} for s in skills],
        "experiences": [{
            "company": e.company, "title": e.title, "location": e.location,
            "start_date": e.start_date, "end_date": e.end_date,
            "bullets": json.loads(e.bullets_json or "[]")
        } for e in experiences],
        "educations": [{
            "institution": ed.institution, "degree": ed.degree, "field": ed.field_of_study
        } for ed in educations],
        "projects": [{
            "title": p.title, "description": p.description, "bullets": json.loads(p.bullets_json or "[]")
        } for p in projects]
    }

    base_name = f"CareerForge_{user.full_name or 'Resume'}_{template.replace(' ', '_')}"
    if format == "pdf":
        filename = f"{base_name}.pdf"
        file_path = ResumeExporter.export_pdf(data, filename, template)
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    elif format == "docx":
        filename = f"{base_name}.docx"
        file_path = ResumeExporter.export_docx(data, filename, template)
        return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=filename)
    elif format == "md":
        content = ResumeExporter.export_markdown(data, template)
        return {"format": "md", "content": content}
    else:
        content = ResumeExporter.export_txt(data, template)
        return {"format": "txt", "content": content}
