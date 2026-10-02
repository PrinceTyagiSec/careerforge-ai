from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

class ProviderHealthItem(BaseModel):
    provider_name: str
    status: str
    last_checked_at: Optional[datetime.datetime]
    last_success_at: Optional[datetime.datetime]
    error_message: Optional[str]
    response_latency_ms: Optional[float]
    consecutive_failures: int

class ProviderCredentialUpdate(BaseModel):
    provider_name: str # "adzuna" | "jooble"
    api_key_or_token: Optional[str] = None
    app_id_or_user: Optional[str] = None
    is_enabled: bool = True

class TelegramConfigUpdate(BaseModel):
    bot_token: str
    chat_id: str
    is_enabled: bool = True

class NotificationPrefUpdate(BaseModel):
    min_match_percentage: float = 75.0
    daily_notification_limit: int = 15
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    notify_high_matches: bool = True
    notify_saved_searches: bool = True
    notify_interviews: bool = True

class BackgroundTaskResponse(BaseModel):
    id: int
    task_identifier: str
    task_name: str
    status: str
    started_at: Optional[datetime.datetime]
    completed_at: Optional[datetime.datetime]
    retry_count: int
    error_message: Optional[str]
    result_summary: Optional[str]

    class Config:
        from_attributes = True

class DashboardAnalyticsResponse(BaseModel):
    total_jobs_discovered: int
    total_jobs_saved: int
    total_applied: int
    total_interviews: int
    total_offers: int
    response_rate_pct: float
    top_skill_gaps: List[Dict[str, Any]]
    applications_by_status: Dict[str, int]
    provider_health_summary: List[ProviderHealthItem]
    telegram_connected: bool
    ollama_status: str
    resume_quality_score: Optional[float]
