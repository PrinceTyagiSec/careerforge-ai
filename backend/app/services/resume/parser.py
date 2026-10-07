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
    "summary": [
        "summary",
        "professional summary",
        "career summary",
        "about me",
        "profile",
        "professional profile",
        "objective",
        "career objective",
    ],

    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "technologies",
        "technical expertise",
        "skill set",
        "tools & technologies",
        "tools and technologies",
        "key skills",
    ],

    "experience": [
        "experience",
        "work experience",
        "employment history",
        "professional experience",
        "work history",
        "career history",
        "professional background",
    ],

    "education": [
        "education",
        "academic background",
        "educational qualifications",
        "educational background",
        "academics",
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "key projects",
        "selected projects",
    ],

    "certifications": [
        "certifications",
        "licenses & certifications",
        "licenses and certifications",
        "credentials",
        "certificates",
        "professional certifications",
    ],

    "achievements": [
        "achievements",
        "honors & awards",
        "honors and awards",
        "awards",
        "accomplishments",
        "recognition",
    ],

    "languages": [
        "languages",
        "language",
        "spoken languages",
        "language proficiency",
    ],

    "publications": [
        "publications",
        "research publications",
        "papers",
        "research papers",
    ],

    "volunteering": [
        "volunteering",
        "volunteer experience",
        "volunteer work",
        "community involvement",
    ],
    "security_experience": [
    "ctf & lab experience",
    "ctf and lab experience",
    "capture the flag",
    "capture the flag experience",
    "lab experience",
    "security lab experience",
    "security labs",
    "hands-on security experience",
    "offensive security experience",
],

"security_research": [
    "vulnerability research",
    "security research",
    "vulnerability research & responsible disclosure",
    "responsible disclosure",
    "bug bounty",
    "bug bounty experience",
    "vulnerability disclosures",
],

    "activities": [
        "activities",
        "extracurricular activities",
        "extracurricular",
        "professional activities",
    ],

    "interests": [
        "interests",
        "hobbies",
        "personal interests",
    ],

    "references": [
        "references",
        "professional references",
    ],
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

        # Certifications
        cert_lines = sections_detected.get("certifications", {}).get("lines", [])
        parsed_certifications = cls._parse_certification_blocks(cert_lines)

        for cert_idx, cert_data in enumerate(parsed_certifications):
            certification = Certification(
                resume_id=resume.id,
                name=cert_data["name"],
                issuing_organization=cert_data["issuing_organization"] or "Unknown",
                issue_date=cert_data.get("issue_date"),
                expiration_date=cert_data.get("expiration_date"),
                credential_url=cert_data.get("credential_url"),
            )

            db.add(certification)
            db.flush()

            claim = Claim(
                resume_id=resume.id,
                category="certification",
                statement=cert_data["name"],
                source_section="Certifications",
                source_snippet=" | ".join(
                    value
                    for value in [
                        cert_data.get("name"),
                        cert_data.get("issuing_organization"),
                        cert_data.get("issue_date"),
                    ]
                    if value
                ),
                verification_status="Extracted",
                confidence=1.0,
            )

            db.add(claim)

        # Achievements
        achievement_lines = (
    sections_detected.get("achievements", {}).get("lines", [])
    or sections_detected.get("security_research", {}).get("lines", [])
)
        parsed_achievements = cls._parse_achievement_blocks(achievement_lines)

        for achievement_idx, achievement_data in enumerate(parsed_achievements):
            achievement = Achievement(
                resume_id=resume.id,
                title=achievement_data["title"],
                description=achievement_data.get("description") or None,
                date=achievement_data.get("date"),
            )

            db.add(achievement)
            db.flush()

            claim = Claim(
                resume_id=resume.id,
                category="achievement",
                statement=achievement_data["title"],
                source_section=(
    "Achievements"
    if sections_detected.get("achievements", {}).get("lines")
    else "Security Research"
),
                source_snippet=(
                    achievement_data["title"]
                    + (
                        " - " + achievement_data["description"]
                        if achievement_data.get("description")
                        else ""
                    )
                ),
                verification_status="Extracted",
                confidence=1.0,
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

    @classmethod
    def _parse_certification_blocks(
        cls,
        lines: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Parse certification entries generically.

        Expected loose patterns:
            Certification Name
            Issuing Organization
            Date

        or:
            Certification Name - Issuing Organization
            Date

        or:
            Certification Name | Issuing Organization | Date

        The parser does not depend on any specific certification name.
        """
        certifications: List[Dict[str, Any]] = []

        date_pattern = re.compile(
            r"""
            \b
            (?:
                Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|
                May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|
                Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?
            )
            \s+\d{4}
            |
            \b\d{4}\b
            """,
            re.IGNORECASE | re.VERBOSE
        )

        url_pattern = re.compile(
            r"https?://\S+|www\.\S+",
            re.IGNORECASE
        )

        cleaned_lines = [
            line.strip()
            for line in lines
            if line.strip() and not re.fullmatch(r"\d+\s*/\s*\d+", line.strip())
        ]

        i = 0

        while i < len(cleaned_lines):
            line = cleaned_lines[i]

            credential_url = None
            url_match = url_pattern.search(line)

            if url_match:
                credential_url = url_match.group(0).rstrip(".,;")
                line = url_pattern.sub("", line).strip(" -|,")
            
            issue_date = None
            expiration_date = None

            date_matches = list(date_pattern.finditer(line))

            if date_matches:
                if len(date_matches) >= 2:
                    issue_date = date_matches[0].group(0)
                    expiration_date = date_matches[1].group(0)
                else:
                    issue_date = date_matches[0].group(0)

                line = date_pattern.sub("", line).strip(" -|,")
            
            if not line:
                i += 1
                continue

            name = ""
            issuing_organization = ""

            # Pattern:
            # Certification Name - Organization
            # Certification Name | Organization
            separator_match = re.split(r"\s+[|–—-]\s+|\s*\|\s*", line, maxsplit=1)

            if len(separator_match) == 2:
                name = separator_match[0].strip(" -|–—")
                issuing_organization = separator_match[1].strip(" -|–—")
            else:
                name = line
                issuing_organization = ""

                # If the next line is short and looks like an organization,
                # treat it as the issuer.
                if i + 1 < len(cleaned_lines):
                    next_line = cleaned_lines[i + 1]

                    next_date = date_pattern.fullmatch(next_line)
                    next_url = url_pattern.fullmatch(next_line)

                    if not next_date and not next_url:
                        if len(next_line.split()) <= 8:
                            issuing_organization = next_line.lstrip("—–- ").strip()
                            i += 1

                if i + 1 < len(cleaned_lines):
                    next_line = cleaned_lines[i + 1]

                    if not issue_date:
                        next_date_match = date_pattern.search(next_line)
                        if next_date_match:
                            issue_date = next_date_match.group(0)
                            i += 1

                    if not credential_url:
                        next_url_match = url_pattern.search(next_line)
                        if next_url_match:
                            credential_url = next_url_match.group(0).rstrip(".,;")
                            i += 1

            if name:
                certifications.append({
                    "name": name,
                    "issuing_organization": issuing_organization,
                    "issue_date": issue_date,
                    "expiration_date": expiration_date,
                    "credential_url": credential_url,
                })

            i += 1

        return certifications


    @classmethod
    def _parse_achievement_blocks(
        cls,
        lines: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Parse generic achievement / award / research entries.

        Supports structures such as:

            Achievement Title
            Organization
            Date
            • Description that may wrap
            onto multiple lines.
            • Another description.

            Next Achievement Title
            Organization
            Date
            • Description.

        The parser uses structural signals rather than
        hard-coded achievement names.
        """

        achievements: List[Dict[str, Any]] = []

        date_pattern = re.compile(
            r"""
            (?:
                (?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|
                May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|
                Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}
                |
                \d{4}
            )
            """,
            re.IGNORECASE | re.VERBOSE
        )

        bullet_pattern = re.compile(r"^[•●▪◦*-]\s*")

        cleaned_lines = [
            line.strip()
            for line in lines
            if line.strip()
            and not re.fullmatch(r"\d+\s*/\s*\d+", line.strip())
        ]

        def is_date_line(value: str) -> bool:
            return bool(date_pattern.fullmatch(value.strip()))

        def looks_like_entry_start(index: int) -> bool:
            """
            Detect whether a non-bullet line starts a new achievement.

            A new achievement normally has:
                title
                organization
                date

            This prevents wrapped bullet lines from being mistaken
            for new achievement titles.
            """
            if index >= len(cleaned_lines):
                return False

            candidate = cleaned_lines[index]

            if bullet_pattern.match(candidate):
                return False

            if index + 1 >= len(cleaned_lines):
                return False

            next_line = cleaned_lines[index + 1]

            # Strong signal:
            # title -> organization -> date
            if index + 2 < len(cleaned_lines):
                third_line = cleaned_lines[index + 2]

                if (
                    not bullet_pattern.match(next_line)
                    and is_date_line(third_line)
                ):
                    return True

            # Also allow:
            # title -> date
            if is_date_line(next_line):
                return True

            return False

        index = 0

        while index < len(cleaned_lines):
            # Skip unexpected non-entry lines until a structural
            # achievement start is found.
            if not looks_like_entry_start(index):
                index += 1
                continue

            title = cleaned_lines[index]
            index += 1

            organization = None
            date_value = None
            description_parts: List[str] = []

            # Optional organization line
            if (
                index < len(cleaned_lines)
                and not bullet_pattern.match(cleaned_lines[index])
                and not is_date_line(cleaned_lines[index])
            ):
                organization = cleaned_lines[index]
                index += 1

            # Optional date line
            if (
                index < len(cleaned_lines)
                and is_date_line(cleaned_lines[index])
            ):
                date_value = cleaned_lines[index]
                index += 1

            # Collect description and wrapped bullet lines.
            while index < len(cleaned_lines):
                current_line = cleaned_lines[index]

                # A structural title after the current achievement
                # means this achievement is finished.
                if (
                    not bullet_pattern.match(current_line)
                    and looks_like_entry_start(index)
                ):
                    break

                if bullet_pattern.match(current_line):
                    bullet_text = bullet_pattern.sub(
                        "",
                        current_line
                    ).strip()

                    if bullet_text:
                        description_parts.append(bullet_text)

                else:
                    # Wrapped continuation of the previous bullet.
                    if description_parts:
                        description_parts.append(current_line)

                index += 1

            description = " ".join(
                part.strip()
                for part in description_parts
                if part.strip()
            ).strip()

            if organization:
                description = (
                    f"{organization}. {description}"
                    if description
                    else organization
                )

            achievements.append({
                "title": title,
                "description": description or None,
                "date": date_value,
            })

        return achievements

    @staticmethod
    def _parse_experience_blocks(
        lines: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Parse professional experience entries from layout-extracted resume lines.

        Handles:
        - title / company / date / location on separate lines
        - date ranges such as "May 2026 – Jul 2026"
        - PDF-wrapped bullet lines
        - semantic subsections such as "CTF & Lab Experience"
        - non-experience sections such as "Languages"
        """

        results: List[Dict[str, Any]] = []

        date_pattern = re.compile(
            r"""
            (?P<start>
                (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)
                [a-z]*\s+\d{4}
                |
                \d{4}
            )
            \s*
            [–—-]
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

        bullet_pattern = re.compile(
            r"^[•●▪◦‣⁃*-]\s*"
        )

        # These are headings inside the Professional Experience section,
        # but they are NOT normal employment entries.
        non_employment_headings = {
            "ctf & lab experience",
            "ctf and lab experience",
            "languages",
            "certifications",
            "certificates",
            "projects",
            "education",
            "skills",
            "achievements",
        }

        def clean_line(value: str) -> str:
            value = value.strip()
            value = bullet_pattern.sub("", value)
            return value.strip()

        def is_location_line(value: str) -> bool:
            value = value.strip()

            if len(value.split()) > 8:
                return False

            location_pattern = re.compile(
                r"""
                ^
                (?:
                    [A-Za-z .'-]+,\s*[A-Za-z .'-]+(?:,\s*[A-Za-z .'-]+)?
                    |
                    (?:India|USA|United States|UK|Canada|Australia)
                )
                $
                """,
                re.IGNORECASE | re.VERBOSE
            )

            return bool(location_pattern.fullmatch(value))

        def finalize_current(current: Optional[Dict[str, Any]]) -> None:
            if not current:
                return

            # Remove accidental empty bullets.
            current["bullets"] = [
                bullet.strip()
                for bullet in current.get("bullets", [])
                if bullet.strip()
            ]

            if current["title"] or current["company"]:
                results.append(current)

        current: Optional[Dict[str, Any]] = None
        pending_bullet: Optional[str] = None

        i = 0

        while i < len(lines):
            raw_line = lines[i].strip()

            if not raw_line:
                i += 1
                continue

            line = clean_line(raw_line)
            normalized = re.sub(r"\s+", " ", line).strip().lower()

            # Stop parsing Professional Experience when another semantic
            # subsection begins.
            if normalized in non_employment_headings:
                if pending_bullet and current:
                    current["bullets"].append(pending_bullet)
                    pending_bullet = None

                finalize_current(current)
                current = None

                # Everything after this heading belongs to another subsection.
                # Do not attempt to parse it as employment.
                break

            date_match = date_pattern.search(line)

            if date_match:
                if pending_bullet and current:
                    current["bullets"].append(pending_bullet)
                    pending_bullet = None

                # A date line marks the end of the metadata for an experience.
                start_date = date_match.group("start").strip()
                end_date = date_match.group("end").strip()

                # Everything before the date may contain title/company.
                metadata = line[:date_match.start()].strip()

                if metadata:
                    parts = [
                        part.strip()
                        for part in re.split(
                            r"\s+[|]\s+|\s+[–—-]\s+",
                            metadata
                        )
                        if part.strip()
                    ]

                    title = parts[0] if parts else "Professional Experience"
                    company = parts[1] if len(parts) > 1 else "Not specified"

                else:
                    # Expected layout:
                    #
                    # Job Title
                    # Company
                    # May 2026 – Jul 2026
                    #
                    # Therefore use the two lines immediately preceding
                    # the date.
                    previous_lines = []

                    j = i - 1

                    while j >= 0 and len(previous_lines) < 2:
                        previous = clean_line(lines[j])

                        if previous:
                            previous_lines.insert(0, previous)

                        j -= 1

                    if len(previous_lines) >= 2:
                        title = previous_lines[-2]
                        company = previous_lines[-1]
                    elif len(previous_lines) == 1:
                        title = previous_lines[0]
                        company = "Not specified"
                    else:
                        title = "Professional Experience"
                        company = "Not specified"

                # If we already had an experience, finalize it.
                finalize_current(current)

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

                i += 1
                continue

            # Nothing can be attached to an experience until its date line
            # has been encountered.
            if not current:
                i += 1
                continue

            # Location normally follows the date.
            if not current["bullets"] and is_location_line(line):
                current["location"] = line
                i += 1
                continue

            has_bullet_marker = bool(bullet_pattern.match(raw_line))

            if has_bullet_marker:
                # Finish the previous wrapped bullet.
                if pending_bullet:
                    current["bullets"].append(pending_bullet)

                pending_bullet = line
            else:
                # A non-bullet line immediately after a bullet is normally
                # a PDF-wrapped continuation of that bullet.
                if pending_bullet:
                    pending_bullet = f"{pending_bullet} {line}".strip()
                else:
                    # Preserve non-bullet descriptive text when present.
                    if line:
                        pending_bullet = line

            i += 1

        if pending_bullet and current:
            current["bullets"].append(pending_bullet)

        finalize_current(current)

        return results

    @staticmethod
    def _parse_education_blocks(lines: List[str]) -> List[Dict[str, Any]]:
        results = []

        degree_patterns = [
            r"\bb\.?\s*tech\b",
            r"\bb\.?\s*e\.?\b",
            r"\bbca\b",
            r"\bm\.?\s*tech\b",
            r"\bmca\b",
            r"\bbachelor\b",
            r"\bmaster\b",
            r"\bph\.?\s*d\.?\b",
            r"\bdiploma\b",
            r"\bassociate\b",
        ]

        month_pattern = (
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*"
        )

        def is_degree_line(value: str) -> bool:
            return any(
                re.search(pattern, value, re.IGNORECASE)
                for pattern in degree_patterns
            )

        def is_date_line(value: str) -> bool:
            value = value.strip()

            return bool(
                re.search(
                    rf"\b{month_pattern}\s+\d{{4}}\b"
                    rf"(?:\s*[–-]\s*"
                    rf"(?:Present|\b{month_pattern}\s+\d{{4}}\b))?",
                    value,
                    re.IGNORECASE,
                )
            )

        def is_location_line(value: str) -> bool:
            value = value.strip()

            if len(value.split()) > 8:
                return False

            return bool(
                re.fullmatch(
                    r"[A-Za-z .'-]+,\s*[A-Za-z .'-]+"
                    r"(?:,\s*[A-Za-z .'-]+)?",
                    value,
                )
            )

        def is_institution_line(value: str) -> bool:
            value_lower = value.lower()

            institution_words = (
                "university",
                "institute",
                "institution",
                "college",
                "school",
                "academy",
                "vidyapeeth",
                "polytechnic",
            )

            return any(word in value_lower for word in institution_words)

        def split_dates(value: str):
            match = re.search(
                rf"({month_pattern}\s+\d{{4}})"
                rf"\s*[–-]\s*"
                rf"(Present|{month_pattern}\s+\d{{4}})",
                value,
                re.IGNORECASE,
            )

            if match:
                return match.group(1).strip(), match.group(2).strip()

            single_match = re.search(
                rf"\b({month_pattern}\s+\d{{4}})\b",
                value,
                re.IGNORECASE,
            )

            if single_match:
                return single_match.group(1).strip(), ""

            return "", ""

        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # An education record starts with a recognizable degree.
            if not is_degree_line(line):
                i += 1
                continue

            degree_lines = [line]
            institution = ""
            location = ""
            start_date = ""
            end_date = ""

            # Collect this education block until another degree starts.
            block = []
            j = i + 1

            while j < len(lines):
                current = lines[j].strip()

                if not current:
                    j += 1
                    continue

                if is_degree_line(current):
                    break

                block.append(current)
                j += 1

            # First identify metadata lines.
            date_index = None

            for index, value in enumerate(block):
                if is_date_line(value):
                    start_date, end_date = split_dates(value)
                    date_index = index
                    break

            for value in block:
                if is_institution_line(value):
                    institution = value
                    break

            for value in block:
                if is_location_line(value):
                    location = value
                    break

            # If the institution wasn't recognized by its name,
            # use the first non-date/non-location line before the date.
            if not institution:
                search_end = date_index if date_index is not None else len(block)

                for value in block[:search_end]:
                    if not is_date_line(value) and not is_location_line(value):
                        institution = value
                        break

            # Any text before the institution is a possible wrapped
            # continuation of the degree.
            if institution:
                institution_index = block.index(institution)

                for value in block[:institution_index]:
                    if (
                        not is_date_line(value)
                        and not is_location_line(value)
                        and value != institution
                    ):
                        degree_lines.append(value)

            degree = " ".join(
                part.strip()
                for part in degree_lines
                if part.strip()
            )

            results.append({
                "institution": institution or "Unknown Institution",
                "degree": degree,
                "field": "",
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
            })

            i = j

        return results

    @staticmethod
    def _parse_project_blocks(lines: List[str]) -> List[Dict[str, Any]]:
        results = []

        def is_date_range(value: str) -> bool:
            return bool(
                re.fullmatch(
                    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                    r"[a-z]*\s+\d{4}\s*[–-]\s*"
                    r"(?:Present|"
                    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                    r"[a-z]*\s+\d{4})",
                    value.strip(),
                    re.IGNORECASE,
                )
            )

        def is_bullet(value: str) -> bool:
            return value.lstrip().startswith(("•", "-", "*"))

        current = None
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Look ahead for the project date.
            # The project title/subtitle may occupy multiple lines.
            date_index = None

            for look_ahead in range(0, 4):
                if i + look_ahead < len(lines):
                    candidate = lines[i + look_ahead].strip()

                    if is_date_range(candidate):
                        date_index = i + look_ahead
                        break

                    if is_bullet(candidate):
                        break

            # A new project starts when a date is found within the next
            # few lines and the current line is not a bullet.
            if date_index is not None and not is_bullet(line):
                if current:
                    results.append(current)

                title = line
                description_parts = []

                # Everything between title and date is the project
                # subtitle/description.
                for k in range(i + 1, date_index):
                    value = lines[k].strip()

                    if value:
                        description_parts.append(value)

                date_value = lines[date_index].strip()

                date_parts = re.split(r"\s*[–-]\s*", date_value, maxsplit=1)

                current = {
                    "title": title,
                    "description": " ".join(description_parts),
                    "bullets": [],
                    "technologies": [],
                    "start_date": date_parts[0].strip(),
                    "end_date": date_parts[1].strip() if len(date_parts) > 1 else "",
                }

                i = date_index + 1
                continue

            if current:
                clean = line.lstrip("•-*• \t").strip()

                if clean:
                    if is_bullet(line):
                        # Start a new bullet.
                        current["bullets"].append(clean)
                    elif current["bullets"]:
                        # PDF line wrapping: append continuation text
                        # to the previous bullet instead of creating
                        # another bullet.
                        current["bullets"][-1] += " " + clean
                    elif not current["description"]:
                        current["description"] = clean
                    else:
                        current["description"] += " " + clean

            i += 1

        if current:
            results.append(current)

        return results