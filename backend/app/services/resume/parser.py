import re
import json
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models.resume import (
    Resume, ResumeSection, ResumeVersion, Skill, Experience,
    Education, Project, Certification, Achievement, Claim
)
from app.models.user import User, CandidateProfile
from app.services.job_quality.normalizer import JobNormalizer

class ResumeParser:
    """
    Deterministic Resume Section and Entity Parser.
    Extracts structured sections, contacts, skills, work history,
    education, and atomic claims for fact protection.
    """
    SECTION_HEADERS = {
        "summary": ["summary", "professional summary", "about me", "profile", "objective", "career objective"],
        "skills": ["skills", "technical skills", "core competencies", "technologies", "skill set", "tools & technologies"],
        "experience": ["experience", "work experience", "employment history", "professional experience", "work history"],
        "education": ["education", "academic background", "educational qualifications", "academics"],
        "projects": ["projects", "personal projects", "academic projects", "key projects"],
        "certifications": ["certifications", "licenses & certifications", "credentials", "certificates"],
        "achievements": ["achievements", "honors & awards", "awards", "accomplishments"]
    }

    @classmethod
    def parse_and_populate(cls, db: Session, resume: Resume, user: User) -> Dict[str, Any]:
        text = resume.raw_text or ""
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 1. Contact / Header Info Extraction
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        phone_match = re.search(r'(?:\+91[\s-]?)?[6789]\d{9}', text) # Indian mobile format
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)

        # 2. Section Partitioning
        sections_detected = cls._partition_sections(lines)
        print("\n========== DEBUG RESUME ==========")
        print("RAW TEXT:")
        print(resume.raw_text)

        print("\nLINES:")
        for i, line in enumerate(lines):
            print(i, repr(line))

        print("\nSECTIONS:")
        for key, value in sections_detected.items():
            print("\nSECTION:", key)
            print("HEADING:", value.get("heading"))
            for line in value.get("lines", []):
                print("  ", repr(line))

        print("==================================\n")

        # Clear existing parsed entities for this resume
        db.query(ResumeSection).filter(ResumeSection.resume_id == resume.id).delete()
        db.query(Skill).filter(Skill.resume_id == resume.id).delete()
        db.query(Experience).filter(Experience.resume_id == resume.id).delete()
        db.query(Education).filter(Education.resume_id == resume.id).delete()
        db.query(Project).filter(Project.resume_id == resume.id).delete()
        db.query(Certification).filter(Certification.resume_id == resume.id).delete()
        db.query(Achievement).filter(Achievement.resume_id == resume.id).delete()
        db.query(Claim).filter(Claim.resume_id == resume.id).delete()

        # 3. Store Structured Sections
        for order_idx, (sec_type, sec_data) in enumerate(sections_detected.items()):
            sec_obj = ResumeSection(
                resume_id=resume.id,
                section_type=sec_type,
                heading=sec_data["heading"],
                order_index=order_idx,
                content="\n".join(sec_data["lines"]),
                is_enabled=True
            )
            db.add(sec_obj)

        # 4. Extract Skills & Create Claims
        skills_text = "\n".join(sections_detected.get("skills", {}).get("lines", []))
        all_skills = JobNormalizer.extract_skills_from_text(skills_text if skills_text else text)
        
        for sk in all_skills:
            skill_obj = Skill(
                resume_id=resume.id,
                name=sk["name"],
                canonical_name=sk["canonical_name"],
                category=sk["category"],
                proficiency="Advanced" if sk["canonical_name"] in ["Python", "JavaScript", "SQL"] else "Intermediate",
                verification_status="Verified"
            )
            db.add(skill_obj)

            # Atomic claim
            claim = Claim(
                resume_id=resume.id,
                category="skill",
                statement=f"Proficient in {sk['canonical_name']}",
                source_section="Skills",
                source_snippet=sk["name"],
                verification_status="Verified",
                confidence=1.0
            )
            db.add(claim)

        # 5. Extract Experience
        exp_lines = sections_detected.get("experience", {}).get("lines", [])
        print("\n========== EXPERIENCE DEBUG ==========")
        print("exp_lines =", exp_lines)

        parsed_experiences = cls._parse_experience_blocks(exp_lines)

        print("parsed_experiences =", parsed_experiences)
        print("experience count =", len(parsed_experiences))
        print("======================================\n")
        parsed_experiences = cls._parse_experience_blocks(exp_lines)
        for idx, exp in enumerate(parsed_experiences):
            exp_obj = Experience(
                resume_id=resume.id,
                company=exp["company"],
                title=exp["title"],
                location=exp.get("location", "India"),
                start_date=exp.get("start_date", "2023"),
                end_date=exp.get("end_date", "Present"),
                is_current=exp.get("is_current", True),
                description=exp.get("description", ""),
                bullets_json=json.dumps(exp.get("bullets", [])),
                order_index=idx
            )
            db.add(exp_obj)

            # Atomic claims for each bullet
            for b_idx, bullet in enumerate(exp.get("bullets", [])):
                claim = Claim(
                    resume_id=resume.id,
                    category="experience",
                    statement=bullet,
                    source_section=f"Experience -> {exp['company']} -> Bullet {b_idx + 1}",
                    source_snippet=bullet[:150],
                    verification_status="Verified",
                    confidence=1.0
                )
                db.add(claim)

        # 6. Extract Education
        edu_lines = sections_detected.get("education", {}).get("lines", [])
        parsed_education = cls._parse_education_blocks(edu_lines)
        for idx, edu in enumerate(parsed_education):
            edu_obj = Education(
                resume_id=resume.id,
                institution=edu["institution"],
                degree=edu["degree"],
                field_of_study=edu.get("field", "Computer Science"),
                start_date=edu.get("start_date", ""),
                end_date=edu.get("end_date", ""),
                order_index=idx
            )
            db.add(edu_obj)
            claim = Claim(
                resume_id=resume.id,
                category="education",
                statement=f"{edu['degree']} from {edu['institution']}",
                source_section="Education",
                source_snippet=edu["institution"],
                verification_status="Verified",
                confidence=1.0
            )
            db.add(claim)

        # 7. Extract Projects
        proj_lines = sections_detected.get("projects", {}).get("lines", [])
        parsed_projects = cls._parse_project_blocks(proj_lines)
        for idx, proj in enumerate(parsed_projects):
            proj_obj = Project(
                resume_id=resume.id,
                title=proj["title"],
                description=proj.get("description", ""),
                technologies_json=json.dumps(proj.get("technologies", [])),
                bullets_json=json.dumps(proj.get("bullets", [])),
                order_index=idx
            )
            db.add(proj_obj)
            claim = Claim(
                resume_id=resume.id,
                category="project",
                statement=f"Built project: {proj['title']}",
                source_section="Projects",
                source_snippet=proj['title'],
                verification_status="Verified",
                confidence=1.0
            )
            db.add(claim)

        # 8. Create or Update Default ResumeVersion
        master_version = db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume.id).first()
        if not master_version:
            master_version = ResumeVersion(
                resume_id=resume.id,
                version_number=1,
                name="Master Resume",
                is_active=True,
                template_name="ATS Simple"
            )
            db.add(master_version)

        # 9. Update CandidateProfile automatically without overwriting manual edits
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        if not profile:
            profile = CandidateProfile(user_id=user.id)
            db.add(profile)

        # Populate empty profile fields safely
        if not profile.headline and parsed_experiences:
            profile.headline = parsed_experiences[0]["title"]
            profile.target_role = parsed_experiences[0]["title"]
        if not profile.summary and "summary" in sections_detected:
            profile.summary = " ".join(sections_detected["summary"]["lines"])
        if not profile.linkedin_url and linkedin_match:
            profile.linkedin_url = f"https://{linkedin_match.group(0)}"
        if not profile.github_url and github_match:
            profile.github_url = f"https://{github_match.group(0)}"
        if not profile.phone and phone_match:
            profile.phone = phone_match.group(0)

        # Calculate estimated years of experience
        exp_min, _ = JobNormalizer.extract_experience_years(text)
        if exp_min:
            profile.years_of_experience = exp_min
        elif parsed_experiences:
            profile.years_of_experience = max(1.0, float(len(parsed_experiences) * 1.5))

        resume.parsing_status = "parsed"
        db.commit()

        return {
            "skills_count": len(all_skills),
            "experiences_count": len(parsed_experiences),
            "education_count": len(parsed_education),
            "projects_count": len(parsed_projects),
            "claims_count": db.query(Claim).filter(Claim.resume_id == resume.id).count()
        }

    @classmethod
    def _partition_sections(
        cls,
        lines: List[str]
    ) -> Dict[str, Dict[str, Any]]:

        sections: Dict[str, Dict[str, Any]] = {}

        current_section = "summary"
        sections[current_section] = {
            "heading": "Professional Summary",
            "lines": []
        }

        # Build normalized lookup
        header_lookup = {}

        for section_type, headers in cls.SECTION_HEADERS.items():
            for header in headers:
                normalized = re.sub(
                    r"[^a-z0-9\s&]",
                    "",
                    header.lower()
                ).strip()

                normalized = re.sub(r"\s+", " ", normalized)

                header_lookup[normalized] = section_type

        for raw_line in lines:
            line = raw_line.strip()

            if not line:
                continue

            normalized_line = re.sub(
                r"[^a-z0-9\s&]",
                "",
                line.lower()
            ).strip()

            normalized_line = re.sub(
                r"\s+",
                " ",
                normalized_line
            )

            detected = header_lookup.get(normalized_line)

            if detected:
                current_section = detected

                if current_section not in sections:
                    sections[current_section] = {
                        "heading": line,
                        "lines": []
                    }

                continue

            sections[current_section]["lines"].append(line)

        return {
            key: value
            for key, value in sections.items()
            if value["lines"]
        }

    @staticmethod
    def _parse_experience_blocks(
        lines: List[str]
    ) -> List[Dict[str, Any]]:

        results = []

        date_pattern = re.compile(
            r"""
            (?P<start>
                (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)
                [a-z]*\s+\d{4}
                |
                \d{4}
            )
            \s*
            [–—\-]
            \s*
            (?P<end>
                Present
                |
                (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)
                [a-z]*\s+\d{4}
                |
                \d{4}
            )
            """,
            re.IGNORECASE | re.VERBOSE
        )

        current = None

        for i, line in enumerate(lines):

            clean_line = line.strip()

            if not clean_line:
                continue

            # Remove bullet marker
            clean_line = re.sub(
                r"^[•●▪◦\-\*]\s*",
                "",
                clean_line
            ).strip()

            date_match = date_pattern.search(clean_line)

            if date_match:

                # Finalize previous experience
                if current:
                    results.append(current)

                start_date = date_match.group("start")
                end_date = date_match.group("end")

                # Everything before the date is metadata
                metadata = clean_line[:date_match.start()].strip()

                # If date is on its own line, use previous lines
                if not metadata:
                    previous = lines[max(0, i - 2):i]

                    previous = [
                        re.sub(
                            r"^[•●▪◦\-\*]\s*",
                            "",
                            p.strip()
                        )
                        for p in previous
                        if p.strip()
                    ]

                    if len(previous) >= 2:
                        title = previous[-2]
                        company = previous[-1]
                    elif len(previous) == 1:
                        title = previous[0]
                        company = "Not specified"
                    else:
                        title = "Professional Experience"
                        company = "Not specified"

                else:
                    # Handle:
                    # Job Title | Company | May 2026 - Jul 2026
                    parts = re.split(
                        r"\s+[|•]\s+|\s+[–—]\s+",
                        metadata
                    )

                    title = parts[0].strip()

                    company = (
                        parts[1].strip()
                        if len(parts) > 1
                        else "Not specified"
                    )

                current = {
                    "title": title,
                    "company": company,
                    "location": "India",
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_current": end_date.lower() == "present",
                    "bullets": [],
                    "description": ""
                }

                continue

            # Detect location after creating experience
            if current:
                # Don't treat obvious location lines as bullets
                if re.search(
                    r"(India|USA|United States|UK|Canada|Australia)$",
                    clean_line,
                    re.IGNORECASE
                ) and len(clean_line.split()) <= 8:

                    current["location"] = clean_line
                    continue

                current["bullets"].append(clean_line)

        if current:
            results.append(current)

        return results

    @staticmethod
    def _parse_education_blocks(lines: List[str]) -> List[Dict[str, Any]]:
        results = []
        for line in lines:
            if re.search(r'(b\.tech|bachelor|master|m\.tech|degree|university|institute|college|b\.e|bca|mca)', line, re.IGNORECASE):
                results.append({
                    "institution": line,
                    "degree": "Bachelor of Technology / Degree",
                    "field": "Computer Science & Engineering"
                })
        if not results and lines:
            results.append({
                "institution": lines[0],
                "degree": "Graduate Degree",
                "field": "Engineering / Technology"
            })
        return results

    @staticmethod
    def _parse_project_blocks(lines: List[str]) -> List[Dict[str, Any]]:
        results = []
        current = None
        for line in lines:
            if line.isupper() or len(line) < 40 and not line.startswith(("•", "-", "*")):
                if current:
                    results.append(current)
                current = {"title": line, "bullets": [], "technologies": []}
            elif current:
                clean = line.lstrip("•-*• \t")
                if clean:
                    current["bullets"].append(clean)
        if current:
            results.append(current)
        return results
