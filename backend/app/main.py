import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings, UPLOADS_DIR, EXPORTS_DIR
from app.core.database import engine, Base, SessionLocal
from app.core.user_helper import get_or_create_default_user
import app.models # ensure all models are registered

# Import API routers
from app.api.profile import router as profile_router
from app.api.resumes import router as resumes_router
from app.api.jobs import router as jobs_router
from app.api.applications import router as applications_router
from app.api.saved_searches import router as saved_searches_router
from app.api.companies import router as companies_router
from app.api.telegram import router as telegram_router
from app.api.providers import router as providers_router
from app.api.analytics import router as analytics_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Local-First, India-Focused AI Career Operating System"
)

# CORS Middleware for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount exports directory for file downloads
app.mount("/exports", StaticFiles(directory=str(EXPORTS_DIR)), name="exports")

# Include Routers
app.include_router(profile_router, prefix=settings.API_V1_STR)
app.include_router(resumes_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(applications_router, prefix=settings.API_V1_STR)
app.include_router(saved_searches_router, prefix=settings.API_V1_STR)
app.include_router(companies_router, prefix=settings.API_V1_STR)
app.include_router(telegram_router, prefix=settings.API_V1_STR)
app.include_router(providers_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)

# @app.on_event("startup")
# def on_startup():
#     db = SessionLocal()
#     try:
#         user = get_or_create_default_user(db)
#         # Seed initial Indian tech job fixtures if DB has 0 jobs
#         from app.models.job import Job
#         if db.query(Job).count() == 0:
#             from app.services.job_providers.imported import UserImportProvider
#             from app.services.job_providers.manager import JobProviderManager
#             from app.services.matching.engine import MatchingEngine
            
#             mgr = JobProviderManager(db)
#             seed_jobs = [
#                 {
#                     "title": "Senior Python Backend Engineer",
#                     "company_name": "Razorpay",
#                     "location": "Bengaluru, Karnataka",
#                     "salary_min": 1800000.0,
#                     "salary_max": 2800000.0,
#                     "url": "https://razorpay.com/careers/python-backend-engineer",
#                     "description": "We are seeking a Senior Python Backend Engineer to build high-scale payment processing APIs. Requirements: 3-5 years of experience in Python, FastAPI, Django, PostgreSQL, Redis, Docker, and AWS. Strong understanding of REST API design and distributed systems. Location: Bengaluru or Remote India."
#                 },
#                 {
#                     "title": "Full Stack Developer (React & Node.js)",
#                     "company_name": "Swiggy",
#                     "location": "Remote India",
#                     "salary_min": 1400000.0,
#                     "salary_max": 2400000.0,
#                     "url": "https://swiggy.com/careers/fullstack-developer",
#                     "description": "Swiggy is hiring a Full Stack Developer. You will develop customer-facing web applications. Tech stack: React, TypeScript, Node.js, Express.js, MongoDB, Docker, Git. Requires at least 2 years of experience with modern frontend and backend architectures."
#                 },
#                 {
#                     "title": "FastAPI & AI Systems Engineer",
#                     "company_name": "Postman",
#                     "location": "Noida, Uttar Pradesh",
#                     "salary_min": 2000000.0,
#                     "salary_max": 3200000.0,
#                     "url": "https://postman.com/careers/fastapi-ai-systems",
#                     "description": "Build next-generation developer tooling at Postman. Required: Python, FastAPI, Machine Learning, PyTorch, Docker, Kubernetes, CI/CD, PostgreSQL, and Linux. Experience designing high-throughput API gateways and microservices in India."
#                 },
#                 {
#                     "title": "Cybersecurity & Cloud Security Specialist",
#                     "company_name": "Tata Consultancy Services (TCS)",
#                     "location": "Pune, Maharashtra",
#                     "salary_min": 1200000.0,
#                     "salary_max": 1800000.0,
#                     "url": "https://tcs.com/careers/cybersecurity-cloud",
#                     "description": "Looking for Cloud Security and Infosec analysts. Skills required: Cybersecurity, AWS, Linux, Python, Docker, vulnerability scanning, and compliance auditing. 2+ years of enterprise experience."
#                 },
#                 {
#                     "title": "Junior Python / Django Developer",
#                     "company_name": "Zomato",
#                     "location": "Gurugram, Haryana",
#                     "salary_min": 800000.0,
#                     "salary_max": 1400000.0,
#                     "url": "https://zomato.com/careers/junior-python-dev",
#                     "description": "Join Zomato's logistics platform team. Tech: Python, Django, SQL, PostgreSQL, Git, REST API. 0-2 years of experience. Ideal for early-career developers with strong problem-solving skills in data structures."
#                 }
#             ]
#             for sj in seed_jobs:
#                 item = UserImportProvider.import_from_text(
#                     title=sj["title"],
#                     company_name=sj["company_name"],
#                     description=sj["description"],
#                     location=sj["location"],
#                     salary_min=sj["salary_min"],
#                     salary_max=sj["salary_max"],
#                     url=sj["url"]
#                 )
#                 j = mgr.ingest_provider_item(item)
#                 if j:
#                     matcher = MatchingEngine(db, user)
#                     matcher.match_job(j)

#     finally:
#         db.close()

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        get_or_create_default_user(db)
    finally:
        db.close()

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "market": "India",
        "local_first": True
    }
