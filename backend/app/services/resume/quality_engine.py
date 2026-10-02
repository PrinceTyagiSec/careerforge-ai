import re
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models.resume import Resume, Skill, Experience, Education, Project

class ResumeQualityEngine:
    """
    Dedicated Resume Quality Engine covering Content, Readability, ATS, and Completeness.
    Deterministic, rigorous, and actionable. Never invents missing facts.
    """

    WEAK_VERBS = [
        "helped", "assisted", "worked on", "handled", "was responsible for",
        "involved in", "did", "participated in", "supported", "contributed to"
    ]

    ACTION_VERBS = [
        "architected", "engineered", "built", "spearheaded", "optimized",
        "accelerated", "deployed", "scaled", "reduced", "increased", "designed"
    ]

    @classmethod
    def analyze(cls, db: Session, resume: Resume) -> Dict[str, Any]:
        text = resume.raw_text or ""
        skills = db.query(Skill).filter(Skill.resume_id == resume.id).all()
        experiences = db.query(Experience).filter(Experience.resume_id == resume.id).all()
        educations = db.query(Education).filter(Education.resume_id == resume.id).all()
        projects = db.query(Project).filter(Project.resume_id == resume.id).all()

        content_issues = []
        readability_issues = []
        ats_issues = []
        completeness_issues = []

        content_score = 100
        readability_score = 100
        ats_score = 100
        completeness_score = 100

        # --- 1. Content Analysis ---
        all_bullets = []
        for exp in experiences:
            import json
            try:
                bullets = json.loads(exp.bullets_json or "[]")
                all_bullets.extend(bullets)
            except Exception:
                pass

        weak_bullet_count = 0
        metric_bullet_count = 0
        for b in all_bullets:
            b_lower = b.lower()
            if any(wv in b_lower for wv in cls.WEAK_VERBS):
                weak_bullet_count += 1
            if re.search(r'\b(?:\d+[\%xX]?|\$\d+|\₹\d+|reduced|increased|improved by)\b', b):
                metric_bullet_count += 1

        if weak_bullet_count > 0:
            content_issues.append({
                "severity": "medium",
                "message": f"Found {weak_bullet_count} bullet(s) using passive/weak language (e.g., 'helped', 'worked on'). Replace with active achievement verbs (e.g., 'architected', 'optimized')."
            })
            content_score -= min(25, weak_bullet_count * 5)

        if all_bullets and (metric_bullet_count / len(all_bullets)) < 0.35:
            content_issues.append({
                "severity": "high",
                "message": "Only a few bullets contain quantifiable metrics or measurable outcomes (%, numbers, scale). Quantify your impact wherever possible."
            })
            content_score -= 20

        if not resume.raw_text or len(resume.raw_text.split()) < 150:
            content_issues.append({
                "severity": "high",
                "message": "Resume content appears sparse (less than 150 words). Provide detailed technical contributions and project impact."
            })
            content_score -= 30

        # --- 2. Readability Analysis ---
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        overly_long_bullets = [b for b in all_bullets if len(b.split()) > 45]
        if overly_long_bullets:
            readability_issues.append({
                "severity": "medium",
                "message": f"Found {len(overly_long_bullets)} overly long bullet points (>45 words). Bullet points should be concise, ideally 15-30 words."
            })
            readability_score -= min(20, len(overly_long_bullets) * 5)

        # Inconsistent capitalization in headings or bullets
        non_capitalized_bullets = [b for b in all_bullets if b and b[0].islower()]
        if non_capitalized_bullets:
            readability_issues.append({
                "severity": "low",
                "message": f"{len(non_capitalized_bullets)} bullet points begin with a lowercase letter. Maintain uniform capitalization."
            })
            readability_score -= 10

        # --- 3. ATS Analysis ---
        if resume.ocr_applied:
            ats_issues.append({
                "severity": "warning",
                "message": "Resume required OCR processing. Scanned image resumes or complex non-selectable PDFs can cause severe ATS parsing failures."
            })
            ats_score -= 25

        # Check for unsupported characters or excessive symbols
        weird_chars = re.findall(r'[^\x00-\x7F\u2013\u2014\u2022\u20AC\u20B9]', text)
        if len(weird_chars) > 20:
            ats_issues.append({
                "severity": "medium",
                "message": "Detected unusual non-standard unicode characters or decorative icons that can break ATS text extractors."
            })
            ats_score -= 15

        if len(skills) < 5:
            ats_issues.append({
                "severity": "high",
                "message": "Fewer than 5 distinct technical skills identified. Modern ATS relies heavily on keyword matching."
            })
            ats_score -= 20

        # --- 4. Completeness Analysis ---
        has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text))
        has_phone = bool(re.search(r'(?:\+91[\s-]?)?[6789]\d{9}', text))
        has_links = bool(re.search(r'(github|linkedin|portfolio)\.com', text, re.IGNORECASE))

        if not has_email:
            completeness_issues.append({"severity": "critical", "message": "No valid email address detected on resume."})
            completeness_score -= 25
        if not has_phone:
            completeness_issues.append({"severity": "high", "message": "No phone number detected on resume."})
            completeness_score -= 15
        if not has_links:
            completeness_issues.append({"severity": "medium", "message": "No GitHub, LinkedIn, or Portfolio link found."})
            completeness_score -= 10

        if not educations:
            completeness_issues.append({"severity": "high", "message": "No Education section detected."})
            completeness_score -= 20
        if not experiences and not projects:
            completeness_issues.append({"severity": "critical", "message": "Neither Work Experience nor Projects detected."})
            completeness_score -= 30

        # Clamp scores
        content_score = max(20, min(100, content_score))
        readability_score = max(30, min(100, readability_score))
        ats_score = max(25, min(100, ats_score))
        completeness_score = max(20, min(100, completeness_score))

        overall_quality = round((content_score * 0.35 + readability_score * 0.20 + ats_score * 0.25 + completeness_score * 0.20), 1)

        return {
            "overall_quality_score": overall_quality,
            "category_scores": {
                "content": content_score,
                "readability": readability_score,
                "ats": ats_score,
                "completeness": completeness_score
            },
            "metrics": {
                "total_skills": len(skills),
                "total_experiences": len(experiences),
                "total_bullets": len(all_bullets),
                "measurable_outcomes_count": metric_bullet_count,
                "word_count": len(text.split())
            },
            "issues": {
                "content": content_issues,
                "readability": readability_issues,
                "ats": ats_issues,
                "completeness": completeness_issues
            }
        }
