import time
import asyncio
import datetime
import httpx
from typing import List, Optional, Dict, Any, Tuple
from app.services.job_providers.base import BaseJobProvider, ProviderJobItem
from app.core.config import settings

class JoobleProvider(BaseJobProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Jooble")
        self.api_key = api_key or settings.JOOBLE_API_KEY
        self.base_url = "https://jooble.org/api"
        self._cache: Dict[str, Tuple[float, List[ProviderJobItem]]] = {}
        self.cache_ttl_seconds = 300
        self.rate_limit_delay = 1.0
        self._last_request_time = 0.0

    async def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    async def search(
        self,
        keywords: Optional[str] = None,
        location: Optional[str] = "India",
        page: int = 1,
        results_per_page: int = 20,
        **kwargs
    ) -> List[ProviderJobItem]:
        if not self.api_key:
            return []

        cache_key = f"{keywords}:{location}:{page}:{results_per_page}"
        if cache_key in self._cache:
            ts, cached_results = self._cache[cache_key]
            if time.time() - ts < self.cache_ttl_seconds:
                return cached_results

        await self._rate_limit()

        endpoint = f"{self.base_url}/{self.api_key}"
        payload = {
            "keywords": keywords or "software developer",
            "location": location or "India",
            "page": page
        }

        retries = 3
        backoff = 1.5

        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=12.0) as client:
                    response = await client.post(endpoint, json=payload, headers={"Content-Type": "application/json"})
                    
                    if response.status_code == 429:
                        await asyncio.sleep(backoff * (attempt + 1))
                        continue

                    if response.status_code == 200:
                        data = response.json()
                        results = []
                        for item in data.get("jobs", []):
                            company = item.get("company", "Unknown Company")
                            title = item.get("title", "Untitled Role")
                            snippet = item.get("snippet", "")
                            link = item.get("link", "")
                            ext_id = str(item.get("id", ""))
                            job_loc = item.get("location", location or "India")
                            salary_str = item.get("salary", "")

                            pub_date = None
                            updated_str = item.get("updated")
                            if updated_str:
                                try:
                                    pub_date = datetime.datetime.fromisoformat(updated_str.replace("Z", "+00:00")).replace(tzinfo=None)
                                except Exception:
                                    pass

                            results.append(ProviderJobItem(
                                provider_name="Jooble",
                                external_id=ext_id,
                                title=title,
                                company_name=company,
                                location=job_loc,
                                description=snippet,
                                url=link,
                                salary_currency="INR",
                                published_at=pub_date,
                                raw_data=item
                            ))

                        self._cache[cache_key] = (time.time(), results)
                        return results
                    else:
                        break
            except (httpx.TimeoutException, httpx.RequestError):
                if attempt < retries - 1:
                    await asyncio.sleep(backoff * (attempt + 1))
                else:
                    break

        return []

    async def check_health(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "provider_name": "Jooble",
                "status": "Unavailable",
                "error_message": "Missing Jooble API Key",
                "latency_ms": 0.0
            }

        start = time.time()
        try:
            endpoint = f"{self.base_url}/{self.api_key}"
            payload = {"keywords": "test", "location": "India", "page": 1}
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(endpoint, json=payload)
                latency = round((time.time() - start) * 1000, 2)
                if res.status_code == 200:
                    return {
                        "provider_name": "Jooble",
                        "status": "Connected",
                        "error_message": None,
                        "latency_ms": latency
                    }
                elif res.status_code == 429:
                    return {
                        "provider_name": "Jooble",
                        "status": "Rate Limited",
                        "error_message": "Rate limit exceeded on Jooble API",
                        "latency_ms": latency
                    }
                else:
                    return {
                        "provider_name": "Jooble",
                        "status": "Failed",
                        "error_message": f"HTTP {res.status_code}: {res.text[:100]}",
                        "latency_ms": latency
                    }
        except Exception as e:
            latency = round((time.time() - start) * 1000, 2)
            return {
                "provider_name": "Jooble",
                "status": "Failed",
                "error_message": str(e),
                "latency_ms": latency
            }
