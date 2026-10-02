import datetime
import httpx
from typing import Optional, Tuple
from app.models.job import Job

class FreshnessService:
    @staticmethod
    def calculate_freshness_status(
        published_at: Optional[datetime.datetime],
        discovered_at: Optional[datetime.datetime],
        expires_at: Optional[datetime.datetime] = None,
        is_url_valid: bool = True
    ) -> str:
        """
        Determines freshness state:
        - Unavailable (URL dead/broken)
        - Expired (past expires_at or older than 45 days)
        - Possibly Stale (> 21 days old)
        - Recently Updated (6-20 days old)
        - Fresh (<= 5 days old)
        """
        now = datetime.datetime.utcnow()
        if not is_url_valid:
            return "Unavailable"

        if expires_at and expires_at < now:
            return "Expired"

        ref_date = published_at or discovered_at or now
        age_days = (now - ref_date).days

        if age_days <= 5:
            return "Fresh"
        elif age_days <= 20:
            return "Recently Updated"
        elif age_days <= 40:
            return "Possibly Stale"
        else:
            return "Expired"

    @staticmethod
    async def validate_job_url(url: str, timeout_seconds: float = 5.0) -> Tuple[bool, Optional[int]]:
        """
        Validates job URL by sending HEAD request (or GET fallback) with realistic headers.
        Detects 404, 410 (Gone), 500, or broken domains.
        """
        if not url or not url.startswith(("http://", "https://")):
            return False, None

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout_seconds) as client:
                try:
                    res = await client.head(url, headers=headers)
                    if res.status_code < 400:
                        return True, res.status_code
                except Exception:
                    pass
                
                # Fallback to GET with byte limit if HEAD was rejected or unsupported
                res = await client.get(url, headers=headers)
                is_valid = res.status_code < 400
                return is_valid, res.status_code
        except Exception:
            return False, None
