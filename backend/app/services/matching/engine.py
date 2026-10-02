import json
import datetime
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.job import Job, JobRequirement
from app.models.user import User, CandidateProfile, JobPreference
from app.models.resume import Resume, Skill, Experience, Claim
from app.models.matching import JobMatch, MatchEvidence
from app.services.job_quality.normalizer import JobNormalizer, SKILL_TAXONOMY

class MatchingEngine:
    """
    Hybrid Deterministic & Evidence-backed Matching Engine.
    Configurable weights, verifiable evidence links, personalized ranking,
    and gap analysis.
    """
    DEFAULT_WEIGHTS = {
        "skills": 0.45,
        "experience": 0.20,
        "location": 0.15,
        "title": 0.10,
        "salary": 0.10
    }

    def __init__(self, db: Session, user: User, weights: Optional[Dict[str, float]] = None):
        self.db = db
        self.user = user
        self.weights = weights or self.DEFAULT_WEIGHTS

    def match_job(self, job: Job, candidate_skills: Optional[List[Skill]] = None) -> JobMatch:
        """
        Calculates deterministic match score and builds traceable evidence items.
        """
        profile = self.user.profile
        
        # 1. Gather candidate skills and claims
        if candidate_skills is None:
            active_resume = self.db.query(Resume).filter(Resume.user_id == self.user.id).order_by(Resume.created_at.desc()).first()
            if active_resume:
                candidate_skills = self.db.query(Skill).filter(Skill.resume_id == active_resume.id).all()
                candidate_experiences = self.db.query(Experience).filter(Experience.resume_id == active_resume.id).all()
                candidate_claims = self.db.query(Claim).filter(Claim.resume_id == active_resume.id).all()
            else:
                candidate_skills = []
                candidate_experiences = []
                candidate_claims = []
        else:
            candidate_experiences = []
            candidate_claims = []

        cand_skill_map = {s.canonical_name.lower(): s for s in candidate_skills}

        # 2. Extract job requirements
        job_reqs = self.db.query(JobRequirement).filter(JobRequirement.job_id == job.id).all()
        if not job_reqs:
            # If not yet extracted in DB, extract on the fly
            extracted = JobNormalizer.extract_skills_from_text(f"{job.title} {job.description}")
            job_reqs = []
            for item in extracted:
                r = JobRequirement(
                    job_id=job.id,
                    category=item["category"],
                    requirement_text=item["name"],
                    canonical_term=item["canonical_name"],
                    is_mandatory=True
                )
                self.db.add(r)
                job_reqs.append(r)
            self.db.commit()

        # 3. Calculate Skill Match & Evidence
        matched_skills = []
        partial_skills = []
        missing_skills = []
        transferable_skills = []
        evidence_items = []

        total_req_weight = 0.0
        earned_skill_weight = 0.0

        for req in job_reqs:
            weight = req.importance_weight or 1.0
            total_req_weight += weight
            req_term = req.canonical_term.lower()

            if req_term in cand_skill_map:
                matched_skill = cand_skill_map[req_term]
                matched_skills.append(req.canonical_term)
                earned_skill_weight += weight
                
                # Find supporting experience or claim
                evidence_ref = "Candidate Profile -> Skills"
                candidate_claim_text = f"Skill: {matched_skill.name} ({matched_skill.proficiency})"
                for exp in candidate_experiences:
                    if req_term in (exp.description or "").lower() or req_term in (exp.bullets_json or "").lower():
                        evidence_ref = f"Resume -> Experience -> {exp.company} ({exp.title})"
                        break

                evidence_items.append({
                    "requirement_term": req.canonical_term,
                    "match_status": "Strong",
                    "candidate_claim": candidate_claim_text,
                    "source_reference": evidence_ref,
                    "confidence": 1.0,
                    "verification_status": matched_skill.verification_status or "Verified"
                })
            else:
                # Check for transferable/related skills in the same category
                req_cat = SKILL_TAXONOMY.get(req.canonical_term, {}).get("category")
                related = [s.canonical_name for s in candidate_skills if s.category == req_cat and req_cat is not None]
                if related:
                    partial_skills.append(req.canonical_term)
                    transferable_skills.append(f"{req.canonical_term} (Related: {', '.join(related[:2])})")
                    earned_skill_weight += weight * 0.4
                    evidence_items.append({
                        "requirement_term": req.canonical_term,
                        "match_status": "Transferable",
                        "candidate_claim": f"Related background in {req_cat}: {', '.join(related[:2])}",
                        "source_reference": "Resume -> Related Category Experience",
                        "confidence": 0.7,
                        "verification_status": "Extracted"
                    })
                else:
                    missing_skills.append(req.canonical_term)
                    evidence_items.append({
                        "requirement_term": req.canonical_term,
                        "match_status": "Missing",
                        "candidate_claim": None,
                        "source_reference": None,
                        "confidence": 0.0,
                        "verification_status": "Job Requirement"
                    })

        skill_score = (earned_skill_weight / total_req_weight * 100.0) if total_req_weight > 0 else 75.0

        # 4. Experience Match
        cand_years = profile.years_of_experience if profile else 1.0
        exp_score = 100.0
        if job.experience_min_years is not None:
            if cand_years >= job.experience_min_years:
                exp_score = 100.0
            elif cand_years >= (job.experience_min_years - 1.0):
                exp_score = 75.0
            else:
                deficit = job.experience_min_years - cand_years
                exp_score = max(20.0, 100.0 - (deficit * 25.0))

        # 5. Location Match
        loc_score = 70.0
        user_remote_pref = profile.remote_preference if profile else "Flexible"
        if job.remote_status == "Remote":
            loc_score = 100.0
        elif user_remote_pref == "Flexible":
            loc_score = 85.0
        elif profile and profile.location and profile.location.lower() in job.location.lower():
            loc_score = 95.0
        elif job.remote_status == "Hybrid" and user_remote_pref in ["Hybrid", "Flexible"]:
            loc_score = 90.0

        # 6. Title / Role Relevance
        title_score = 70.0
        target_role = (profile.target_role or profile.headline or "").lower() if profile else ""
        if target_role:
            words = target_role.split()
            matches = sum(1 for w in words if len(w) > 2 and w in job.title.lower())
            if matches >= 2:
                title_score = 100.0
            elif matches == 1:
                title_score = 80.0

        # 7. Salary Match
        salary_score = 80.0
        if job.salary_min and profile and profile.expected_salary_min:
            if job.salary_min >= profile.expected_salary_min:
                salary_score = 100.0
            elif job.salary_max and job.salary_max >= profile.expected_salary_min:
                salary_score = 85.0
            else:
                salary_score = 50.0

        # Composite Deterministic Score
        w = self.weights
        det_score = (
            (skill_score * w["skills"]) +
            (exp_score * w["experience"]) +
            (loc_score * w["location"]) +
            (title_score * w["title"]) +
            (salary_score * w["salary"])
        )
        det_score = round(min(100.0, max(0.0, det_score)), 1)

        # 8. User Behavioral Personalization (Section 17)
        # Check past user actions: saved jobs, applied jobs, rejected jobs
        behavior_boost = 0.0
        existing_match = self.db.query(JobMatch).filter(
            JobMatch.user_id == self.user.id,
            JobMatch.job_id == job.id
        ).first()

        saved_roles_count = self.db.query(JobMatch).filter(
            JobMatch.user_id == self.user.id,
            JobMatch.is_saved == True
        ).count()

        if saved_roles_count > 3:
            # Check if this company or title has been saved before
            similar_saved = self.db.query(JobMatch).join(Job).filter(
                JobMatch.user_id == self.user.id,
                JobMatch.is_saved == True,
                (Job.normalized_company == job.normalized_company) | (Job.normalized_title == job.normalized_title)
            ).first()
            if similar_saved:
                behavior_boost += 3.0

        overall_score = round(min(100.0, det_score + behavior_boost), 1)

        # 9. Explanation Summary
        explanation_lines = [
            f"Match Score: {overall_score}%",
            f"Strong matches: {', '.join(matched_skills[:5]) if matched_skills else 'None'}",
            f"Candidate Experience: {cand_years} yrs (Job requires: {job.experience_min_years or 0}+ yrs)",
            f"Location: {job.location} ({job.remote_status})",
        ]
        if missing_skills:
            explanation_lines.append(f"Missing skills: {', '.join(missing_skills[:4])}")

        gap_analysis = {
            "strong_matches": matched_skills,
            "partial_matches": partial_skills,
            "missing_skills": missing_skills,
            "transferable_skills": transferable_skills,
            "experience_match": {
                "candidate_years": cand_years,
                "required_years_min": job.experience_min_years,
                "required_years_max": job.experience_max_years,
                "is_qualified": cand_years >= (job.experience_min_years or 0)
            },
            "location_compatibility": {
                "job_location": job.location,
                "remote_status": job.remote_status,
                "candidate_preference": user_remote_pref
            }
        }

        # 10. Persist or Update JobMatch in DB
        if not existing_match:
            job_match = JobMatch(
                user_id=self.user.id,
                job_id=job.id,
                overall_score=overall_score,
                deterministic_score=det_score,
                semantic_score=0.0,
                skill_score=round(skill_score, 1),
                experience_score=round(exp_score, 1),
                location_score=round(loc_score, 1),
                salary_score=round(salary_score, 1),
                matching_skills_json=json.dumps(matched_skills),
                partial_skills_json=json.dumps(partial_skills),
                missing_skills_json=json.dumps(missing_skills),
                transferable_skills_json=json.dumps(transferable_skills),
                explanation_summary="\n".join(explanation_lines),
                gap_analysis_json=json.dumps(gap_analysis),
                calculated_at=datetime.datetime.utcnow()
            )
            self.db.add(job_match)
            self.db.flush()
        else:
            job_match = existing_match
            job_match.overall_score = overall_score
            job_match.deterministic_score = det_score
            job_match.skill_score = round(skill_score, 1)
            job_match.experience_score = round(exp_score, 1)
            job_match.location_score = round(loc_score, 1)
            job_match.salary_score = round(salary_score, 1)
            job_match.matching_skills_json = json.dumps(matched_skills)
            job_match.partial_skills_json = json.dumps(partial_skills)
            job_match.missing_skills_json = json.dumps(missing_skills)
            job_match.transferable_skills_json = json.dumps(transferable_skills)
            job_match.explanation_summary = "\n".join(explanation_lines)
            job_match.gap_analysis_json = json.dumps(gap_analysis)
            job_match.updated_at = datetime.datetime.utcnow()

            # Clear old evidence items
            self.db.query(MatchEvidence).filter(MatchEvidence.job_match_id == job_match.id).delete()

        # Insert new evidence items
        for ev in evidence_items:
            me = MatchEvidence(
                job_match_id=job_match.id,
                requirement_term=ev["requirement_term"],
                match_status=ev["match_status"],
                candidate_claim=ev["candidate_claim"],
                source_reference=ev["source_reference"],
                confidence=ev["confidence"],
                verification_status=ev["verification_status"]
            )
            self.db.add(me)

        self.db.commit()
        self.db.refresh(job_match)
        return job_match
