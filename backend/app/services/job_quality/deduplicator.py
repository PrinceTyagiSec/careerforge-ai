import hashlib
import re
from typing import Optional, Tuple, Set
from sqlalchemy.orm import Session
from app.models.job import Job, JobSource, Company
from app.services.job_quality.normalizer import JobNormalizer

class JobDeduplicator:
    @staticmethod
    def clean_url(url: str) -> str:
        """
        Strips tracking parameters (utm_*, ref, gclid, sessionid) to create canonical URL.
        """
        if not url:
            return ""
        # Remove query tracking params
        clean = re.sub(r'(\?|&)(utm_[^&]+|ref=[^&]+|source=[^&]+|gclid=[^&]+|sessionid=[^&]+)', '', url, flags=re.IGNORECASE)
        clean = clean.rstrip("?&/").lower()
        return clean

    @staticmethod
    def generate_dedup_hash(company_name: str, title: str, location: str) -> str:
        """
        Generates deterministic hash based on normalized company, title, and city.
        """
        norm_company = re.sub(r'[^a-z0-9]', '', company_name.lower())
        norm_title = re.sub(r'[^a-z0-9]', '', title.lower())
        norm_loc = re.sub(r'[^a-z0-9]', '', (location or "").lower())
        
        raw_key = f"{norm_company}:{norm_title}:{norm_loc}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    def text_similarity(text1: str, text2: str) -> float:
        """
        Computes Jaccard similarity between two job descriptions using word tokens.
        """
        def tokenize(text: str) -> Set[str]:
            words = re.findall(r'\b[a-z]{3,}\b', text.lower())
            return set(words)

        tokens1 = tokenize(text1)
        tokens2 = tokenize(text2)
        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        return float(intersection) / float(union) if union > 0 else 0.0

    @classmethod
    def find_duplicate(
        cls,
        db: Session,
        canonical_url: str,
        company_name: str,
        title: str,
        location: str,
        description: str,
        external_id: Optional[str] = None
    ) -> Optional[Job]:
        """
        Checks if a job already exists using multi-signal detection:
        1. Exact canonical URL match
        2. Exact company + title + location hash match
        3. Existing job with same company & title with description similarity >= 0.75
        """
        # Signal 1: Canonical URL
        cleaned_url = cls.clean_url(canonical_url)
        if cleaned_url:
            existing = db.query(Job).filter(Job.canonical_url == cleaned_url).first()
            if existing:
                return existing

        # Signal 2: Dedup Hash
        dedup_hash = cls.generate_dedup_hash(company_name, title, location)
        existing = db.query(Job).filter(Job.dedup_hash == dedup_hash).first()
        if existing:
            return existing

        # Signal 3: Same company + similar title + description similarity >= 0.70
        norm_comp = company_name.strip().lower()
        candidates = db.query(Job).filter(Job.normalized_company == norm_comp).all()
        for cand in candidates:
            # Check title similarity
            cand_title_norm = cand.normalized_title.lower()
            incoming_title_norm = title.strip().lower()
            if cand_title_norm == incoming_title_norm or cand_title_norm in incoming_title_norm or incoming_title_norm in cand_title_norm:
                sim = cls.text_similarity(cand.description, description)
                if sim >= 0.70:
                    return cand

        return None
