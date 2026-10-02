from sqlalchemy.orm import Session
from app.models.user import User, CandidateProfile, JobPreference

def get_or_create_default_user(db: Session) -> User:
    """
    Returns the primary local user for this local-first system.
    Creates default profile and preferences if not present.
    """
    user = db.query(User).filter(User.email == "candidate@careerforge.local").first()
    if not user:
        user = User(
            email="candidate@careerforge.local",
            full_name="Candidate",
            is_active=True
        )
        db.add(user)
        db.flush()

        profile = CandidateProfile(
            user_id=user.id,
            headline="Full Stack Engineer",
            summary="Passionate developer specializing in Python, FastAPI, React, and scalable backend architecture.",
            location="Bengaluru, Karnataka",
            remote_preference="Flexible",
            target_role="Full Stack Developer / Backend Engineer",
            years_of_experience=2.5,
            expected_salary_min=1200000.0, # 12 LPA INR
            expected_salary_max=2200000.0,
            currency="INR"
        )
        db.add(profile)

        pref = JobPreference(
            user_id=user.id,
            preferred_roles='["Software Engineer", "Backend Developer", "Full Stack Developer", "Python Developer"]',
            preferred_locations='["Remote India", "Bengaluru", "Noida", "Gurugram", "Hyderabad", "Pune"]',
            preferred_skills='["Python", "FastAPI", "React", "PostgreSQL", "Docker"]',
            min_salary=1000000.0,
            currency="INR"
        )
        db.add(pref)
        db.commit()
        db.refresh(user)

    return user
