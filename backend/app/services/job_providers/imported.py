import re
import datetime
import httpx
from typing import Optional, Dict, Any
from app.services.job_providers.base import ProviderJobItem
from app.services.job_quality.normalizer import JobNormalizer

class UserImportProvider:
    @staticmethod
    async def import_from_url(url: str) -> ProviderJobItem:
        """
        Safely fetches job page and extracts title, company hint, and description text.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            html = response.text

        # Extract title tag
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        raw_title = title_match.group(1).strip() if title_match else "Imported Job Posting"
        # Clean title (split by |, -, etc.)
        title_parts = re.split(r'[-|•]', raw_title)
        title = title_parts[0].strip()
        company_name = title_parts[1].strip() if len(title_parts) > 1 else "Unknown Employer"

        # Strip html tags to get plain text description
        clean_text = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        clean_text = re.sub(r'<style.*?</style>', '', clean_text, flags=re.DOTALL | re.IGNORECASE)
        clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        description = clean_text[:4000]

        return ProviderJobItem(
            provider_name="URL Import",
            external_id=url,
            title=title,
            company_name=company_name,
            location="India",
            description=description,
            url=url,
            published_at=datetime.datetime.utcnow(),
            raw_data={"source_url": url}
        )

    @staticmethod
    def import_from_text(
        title: str,
        company_name: str,
        description: str,
        location: Optional[str] = "India",
        salary_min: Optional[float] = None,
        salary_max: Optional[float] = None,
        url: Optional[str] = None
    ) -> ProviderJobItem:
        """
        Creates ProviderJobItem from manually entered or pasted job details.
        """
        return ProviderJobItem(
            provider_name="Manual Import",
            external_id=None,
            title=title.strip() if title else "Imported Position",
            company_name=company_name.strip() if company_name else "Unknown Company",
            location=location.strip() if location else "India",
            description=description.strip(),
            url=url.strip() if url else f"urn:local-import:{datetime.datetime.utcnow().timestamp()}",
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency="INR",
            published_at=datetime.datetime.utcnow(),
            raw_data={"import_type": "manual_or_pasted"}
        )
