import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.user_helper import get_or_create_default_user
from app.models.saved_search import SavedSearch
from app.schemas.saved_search import SavedSearchCreate, SavedSearchResponse
from app.services.scheduler.task_runner import BackgroundMonitoringService

router = APIRouter(prefix="/saved-searches", tags=["Saved Searches"])

@router.get("", response_model=list[SavedSearchResponse])
def list_saved_searches(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    searches = db.query(SavedSearch).filter(SavedSearch.user_id == user.id).order_by(desc(SavedSearch.created_at)).all()
    return searches

@router.post("", response_model=SavedSearchResponse)
def create_saved_search(data: SavedSearchCreate, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    search = SavedSearch(
        user_id=user.id,
        name=data.name,
        keywords=data.keywords,
        location=data.location or "Remote India",
        remote_preference=data.remote_preference or "Flexible",
        min_salary=data.min_salary,
        experience_level=data.experience_level,
        frequency_minutes=data.frequency_minutes or 360,
        notify_telegram=data.notify_telegram,
        min_match_threshold=data.min_match_threshold or 75.0,
        is_enabled=True
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    return search

@router.post("/{search_id}/run-now")
async def run_saved_search_now(
    search_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = get_or_create_default_user(db)
    search = db.query(SavedSearch).filter(SavedSearch.id == search_id, SavedSearch.user_id == user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Saved search not found")

    # Run in background task runner
    background_tasks.add_task(BackgroundMonitoringService.run_saved_search_job, search.id)
    return {"message": f"Background monitoring task scheduled for '{search.name}'"}

@router.delete("/{search_id}")
def delete_saved_search(search_id: int, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    search = db.query(SavedSearch).filter(SavedSearch.id == search_id, SavedSearch.user_id == user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Saved search not found")

    db.delete(search)
    db.commit()
    return {"message": "Saved search deleted"}
