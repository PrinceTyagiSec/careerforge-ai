import uuid
import datetime
import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.saved_search import SavedSearch
from app.models.system import BackgroundTask
from app.models.user import User
from app.services.job_providers.manager import JobProviderManager
from app.services.matching.engine import MatchingEngine
from app.services.telegram.notifier import TelegramService

class BackgroundMonitoringService:
    @classmethod
    async def run_saved_search_job(cls, saved_search_id: int):
        """
        Executes the 12-step monitoring pipeline for a saved search.
        """
        task_id = f"task-search-{saved_search_id}-{uuid.uuid4().hex[:6]}"
        db: Session = SessionLocal()
        
        task_record = BackgroundTask(
            task_identifier=task_id,
            task_name=f"Monitoring Saved Search #{saved_search_id}",
            status="Running",
            started_at=datetime.datetime.utcnow()
        )
        db.add(task_record)
        db.commit()

        try:
            saved_search = db.query(SavedSearch).filter(SavedSearch.id == saved_search_id).first()
            if not saved_search or not saved_search.is_enabled:
                task_record.status = "Completed"
                task_record.completed_at = datetime.datetime.utcnow()
                task_record.result_summary = "Search is disabled or not found."
                db.commit()
                return

            user = db.query(User).filter(User.id == saved_search.user_id).first()
            mgr = JobProviderManager(db)

            # 1. Fetch from providers
            found_jobs = await mgr.search_and_ingest(
                keywords=saved_search.keywords,
                location=saved_search.location or "India",
                page=1,
                results_per_page=25
            )

            # 2. Match against candidate
            matcher = MatchingEngine(db, user)
            new_high_matches = []
            
            for job in found_jobs:
                match = matcher.match_job(job)
                if match.overall_score >= (saved_search.min_match_threshold or 75.0):
                    new_high_matches.append((job, match))

            # 3. Dispatch notifications
            notified_count = 0
            if saved_search.notify_telegram:
                for job, match in new_high_matches:
                    sent = await TelegramService.notify_job_alert(db, user.id, job, match)
                    if sent:
                        notified_count += 1

            # 4. Update saved search record
            saved_search.last_run_at = datetime.datetime.utcnow()
            saved_search.next_run_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=saved_search.frequency_minutes)
            saved_search.total_found_count = len(found_jobs)
            saved_search.high_match_count = len(new_high_matches)
            
            task_record.status = "Completed"
            task_record.completed_at = datetime.datetime.utcnow()
            task_record.result_summary = f"Processed {len(found_jobs)} jobs. Found {len(new_high_matches)} high-match roles. Sent {notified_count} alerts."
            db.commit()

        except Exception as e:
            task_record.status = "Failed"
            task_record.completed_at = datetime.datetime.utcnow()
            task_record.error_message = str(e)
            db.commit()
        finally:
            db.close()
