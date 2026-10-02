import json
import datetime
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.job import Job, JobSource, JobRequirement, Company
from app.models.system import ProviderCredential, ProviderHealth
from app.services.job_providers.base import ProviderJobItem
from app.services.job_providers.adzuna import AdzunaProvider
from app.services.job_providers.jooble import JoobleProvider
from app.services.job_quality.normalizer import JobNormalizer
from app.services.job_quality.deduplicator import JobDeduplicator
from app.services.job_quality.freshness import FreshnessService

class JobProviderManager:
    def __init__(self, db: Session):
        self.db = db
        self.providers = []
        self._init_providers()

    def _init_providers(self):
        # Read credentials from DB or fallback
        adzuna_cred = self.db.query(ProviderCredential).filter(ProviderCredential.provider_name == "adzuna").first()
        jooble_cred = self.db.query(ProviderCredential).filter(ProviderCredential.provider_name == "jooble").first()

        adzuna_id = None
        adzuna_key = None
        if adzuna_cred and adzuna_cred.is_enabled:
            adzuna_id = adzuna_cred.app_id_or_user
            adzuna_key = adzuna_cred.api_key_or_token

        jooble_key = None
        if jooble_cred and jooble_cred.is_enabled:
            jooble_key = jooble_cred.api_key_or_token

        self.adzuna = AdzunaProvider(app_id=adzuna_id, app_key=adzuna_key)
        self.jooble = JoobleProvider(api_key=jooble_key)
        self.providers = [self.adzuna, self.jooble]

    async def check_all_providers_health(self) -> List[Dict[str, Any]]:
        """
        Pings all configured providers and updates the ProviderHealth table.
        """
        results = []
        for prov in self.providers:
            health = await prov.check_health()
            results.append(health)
            
            # Persist health record in DB
            db_health = self.db.query(ProviderHealth).filter(ProviderHealth.provider_name == prov.provider_name.lower()).first()
            if not db_health:
                db_health = ProviderHealth(provider_name=prov.provider_name.lower())
                self.db.add(db_health)
                
            db_health.status = health["status"]
            db_health.last_checked_at = datetime.datetime.utcnow()
            db_health.error_message = health["error_message"]
            db_health.response_latency_ms = health["latency_ms"]
            if health["status"] == "Connected":
                db_health.last_success_at = datetime.datetime.utcnow()
                db_health.consecutive_failures = 0
            else:
                db_health.consecutive_failures = (
        db_health.consecutive_failures or 0
    ) + 1

        self.db.commit()
        return results

    async def search_and_ingest(
        self,
        keywords: Optional[str] = None,
        location: Optional[str] = "India",
        page: int = 1,
        results_per_page: int = 20
    ) -> List[Job]:
        """
        Queries all available providers concurrently, normalizes, deduplicates,
        and saves fresh jobs to the database.
        """
        tasks = []
        for prov in self.providers:
            tasks.append(prov.search(keywords=keywords, location=location, page=page, results_per_page=results_per_page))

        provider_results = await asyncio.gather(*tasks, return_exceptions=True)
        all_items: List[ProviderJobItem] = []
        
        for idx, res in enumerate(provider_results):
            prov_name = self.providers[idx].provider_name
            if isinstance(res, list):
                all_items.extend(res)
            elif isinstance(res, Exception):
                # Update failure status
                db_health = self.db.query(ProviderHealth).filter(ProviderHealth.provider_name == prov_name.lower()).first()
                if db_health:
                    db_health.status = "Failed"
                    db_health.error_message = str(res)
                    self.db.commit()

        # Ingest and normalize items
        saved_jobs = []
        for item in all_items:
            job = self.ingest_provider_item(item)
            if job:
                saved_jobs.append(job)

        return saved_jobs

    def ingest_provider_item(self, item: ProviderJobItem) -> Optional[Job]:
        """
        Normalizes a ProviderJobItem, runs deduplication, extracts requirements,
        creates/links Company, and inserts or merges into Job and JobSource.
        """
        # Step 1: Normalization
        norm_title = JobNormalizer.normalize_title(item.title)
        loc_label, city, state, remote_status = JobNormalizer.normalize_location(item.location)
        s_min, s_max, curr = JobNormalizer.normalize_salary(item.salary_min, item.salary_max, item.salary_currency)
        exp_min, exp_max = JobNormalizer.extract_experience_years(item.description)
        canonical_url = JobDeduplicator.clean_url(item.url)
        norm_company = item.company_name.strip().title()

        # Step 2: Deduplication Check
        existing_job = JobDeduplicator.find_duplicate(
            db=self.db,
            canonical_url=canonical_url,
            company_name=norm_company,
            title=norm_title,
            location=loc_label,
            description=item.description,
            external_id=item.external_id
        )

        now = datetime.datetime.utcnow()
        if existing_job:
            # Check if this source attribution already exists
            source_exists = any(s.provider_name.lower() == item.provider_name.lower() for s in existing_job.sources)
            if not source_exists:
                new_source = JobSource(
                    job_id=existing_job.id,
                    provider_name=item.provider_name,
                    external_id=item.external_id,
                    source_url=item.url,
                    raw_data=json.dumps(item.raw_data) if item.raw_data else None,
                    created_at=now
                )
                self.db.add(new_source)

            # Update freshness & last_verified_at
            existing_job.last_verified_at = now
            existing_job.freshness_status = FreshnessService.calculate_freshness_status(
                existing_job.published_at, existing_job.discovered_at, existing_job.expires_at, existing_job.is_url_valid
            )
            self.db.commit()
            return existing_job

        # Step 3: Company resolution
        company = self.db.query(Company).filter(Company.normalized_name == norm_company.lower()).first()
        if not company:
            company = Company(
                name=norm_company,
                normalized_name=norm_company.lower(),
                location=loc_label
            )
            self.db.add(company)
            self.db.flush()

        # Step 4: Create new Job
        dedup_hash = JobDeduplicator.generate_dedup_hash(norm_company, norm_title, loc_label)
        freshness_status = FreshnessService.calculate_freshness_status(
            published_at=item.published_at,
            discovered_at=now,
            is_url_valid=True
        )

        new_job = Job(
            title=item.title,
            normalized_title=norm_title,
            company_name=norm_company,
            normalized_company=norm_company.lower(),
            company_id=company.id,
            location=loc_label,
            city=city,
            state=state,
            country="India",
            remote_status=remote_status,
            salary_min=s_min,
            salary_max=s_max,
            salary_currency=curr,
            employment_type=item.employment_type or "Full-time",
            experience_min_years=exp_min,
            experience_max_years=exp_max,
            description=item.description,
            canonical_url=canonical_url if canonical_url else f"urn:source:{item.provider_name}:{item.external_id or now.timestamp()}",
            dedup_hash=dedup_hash,
            published_at=item.published_at or now,
            discovered_at=now,
            last_verified_at=now,
            freshness_status=freshness_status,
            is_active=True,
            is_url_valid=True,
            raw_payload_json=json.dumps(item.raw_data) if item.raw_data else None
        )
        self.db.add(new_job)
        self.db.flush()

        # Step 5: Add Source Attribution
        source = JobSource(
            job_id=new_job.id,
            provider_name=item.provider_name,
            external_id=item.external_id,
            source_url=item.url,
            raw_data=json.dumps(item.raw_data) if item.raw_data else None,
            created_at=now
        )
        self.db.add(source)

        # Step 6: Extract Structured Requirements
        extracted_skills = JobNormalizer.extract_skills_from_text(f"{item.title} {item.description}")
        for sk in extracted_skills:
            req = JobRequirement(
                job_id=new_job.id,
                category=sk["category"],
                requirement_text=sk["name"],
                canonical_term=sk["canonical_name"],
                is_mandatory=True,
                importance_weight=1.0
            )
            self.db.add(req)

        self.db.commit()
        self.db.refresh(new_job)
        return new_job
